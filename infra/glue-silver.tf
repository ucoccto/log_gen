# ---------------------------------------------
# Silver layer - AWS Glue Data Catalog
# ---------------------------------------------

# 데이터 구조, 위치등 Meta 데이터를 관리하는 서비스
# AWS Glue Data Catalog > database > de-ai-25-loggen-silver-glue-db

# 1. 데이터베이스 구성
resource "aws_glue_catalog_database" "silver" {
    # SQL문 고려하여 _로 표기
    # 디비명
    name = "${lower(replace(var.project_name, "-","_"))}_silver_glue_db"
    #name = "${var.project_name}-silver-glue-db"
}

# 2. 테이블 구성, 데이터베이스 내부에 테이블을 수십개 정의 가능
#    s3 silver에 저장되는 parquet 데이터 한개에 대해 논리적인 테이블 정의
#    이 구조를 기반으로 SQL 수행(athena등) => 특정(특수 목적) 데이터 획득 (향후 배치 프로세싱에서 airflow기반으로 처리)
resource "aws_glue_catalog_table" "silver" {
  # 테이블명
  name = "silver_logs_tbl"
  # 테이블의 원소속(데이터베이스) 설정
  database_name = aws_glue_catalog_database.silver.name
}