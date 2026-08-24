# -*- coding: utf-8 -*-
# flink 앱 엔트리 포인트 (환경설정, 필요한 구성생성)

from __future__ import annotations
import json
import os
from pyflink.table import DataTypes, EnvironmentSettings, TableEnvironment
# 일반 파이썬 함수를 Flink SQL에서 호출 가능하게 등록 처리(UDF : User Defined Function)
from pyflink.table.udf import udf
from transform import clean_event_payload

MANAGED_PROPERTIES_PATH = "/etc/flink/application_properties.json"
IS_LOCAL = bool(os.environ.get("IS_LOCAL"))

# 결과는 문자열로 반환, clean_event라는 함수는 Flink에서 사용하는 SQL 내에서 사용 가능
@udf(result_type=DataTypes.STRING())
def clean_event(payload: str):
    # 정제, 전처리 전담 함수를 래핑
    return clean_event_payload(payload)

def _project_dir() -> str:
    current_dir = os.path.dirname(os.path.realpath(__file__))
    if os.path.basename(current_dir) == "app":
        return os.path.dirname(current_dir)
    return current_dir

def _property_map(properties: list[dict], group_id: str) -> dict:
    for prop in properties:
        if prop.get("PropertyGroupId") == group_id:
            return prop.get("PropertyMap", {})
    raise RuntimeError(f"Runtime property group not found: {group_id}")

def _load_application_properties() -> list[dict]:
    if IS_LOCAL:
        path = os.path.join(_project_dir(), "application_properties.json")
    else:
        path = MANAGED_PROPERTIES_PATH
    if not os.path.isfile(path):
        raise RuntimeError(f"Application properties file not found: {path}")

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)

def _create_table_environment() -> TableEnvironment:
    settings = EnvironmentSettings.in_streaming_mode()
    table_env = TableEnvironment.create(settings)
    if IS_LOCAL:
        jar_path = os.path.join(_project_dir(), "target", "pyflink-dependencies.jar")
        if not os.path.isfile(jar_path):
            raise RuntimeError(
                "Connector JAR not found. Run 'mvn clean package' in the flink directory first."
            )
        jar_uri = "file:///" + jar_path.replace("\\", "/")
        table_env.get_config().get_configuration().set_string("pipeline.jars", jar_uri)
    return table_env

def main() -> None:
    # 순서대로 실행을 위한 절차 진행

    # 1. 스트리밍 모드의 flink  테이블환경(테이블구성, sql 사용) 구성
    table_env = _create_table_environment()
    # 2. application_properties.json(로컬), aws 환경등 정보 로드(설정값)->테라폼으로 구성시 자동생성
    properties = _load_application_properties()

    # 3. 런타임 속성에서 InputStream0 이름의 키네시스 정보 획득. 브론즈 입력
    input_props = _property_map(properties, "InputStream0")
    # 4. 런타임 속성에서 OutputStream0 이름의 키네시스 정보 획득. 실버 출력
    output_props = _property_map(properties, "OutputStream0")

    # 5. 키네시스 arn, 리전, 입력시 어디서부터 읽을 것인지 등 정보 로드
    input_stream_arn = input_props["stream.arn"]
    input_region = input_props["aws.region"]
    input_init_position = input_props.get("flink.source.init.position", "LATEST")
    output_stream_arn = output_props["stream.arn"]
    output_region = output_props["aws.region"]

    # 6. 파이썬 함수 clean_event를 Flink SQL 내부에서 clean_event(..)로 사용하도록 등록
    table_env.create_temporary_system_function("clean_event", clean_event)

    table_env.execute_sql(
        f"""
        CREATE TABLE raw_stream (
            payload STRING
        )
        WITH (
            'connector' = 'kinesis',
            'stream.arn' = '{input_stream_arn}',
            'aws.region' = '{input_region}',
            'source.init.position' = '{input_init_position}',
            'format' = 'raw'
        )
        """
    )
    table_env.execute_sql(
        f"""
        CREATE TABLE silver_stream (
            payload STRING
        )
        WITH (
            'connector' = 'kinesis',
            'stream.arn' = '{output_stream_arn}',
            'aws.region' = '{output_region}',
            'sink.batch.max-size' = '100',
            'format' = 'raw'
        )
        """
    )
    result = table_env.execute_sql(
        """
        INSERT INTO silver_stream
        SELECT cleaned_payload
        FROM (
            SELECT clean_event(payload) AS cleaned_payload
            FROM raw_stream
        )
        WHERE cleaned_payload IS NOT NULL
        """
    )
    if IS_LOCAL:
        result.wait()

if __name__ == "__main__":
    # 프로그램 시작점 -> main 함수 호출 하면서 실행 (함수지향적 프로그램)
    main()