# Silver kinesis -> lambda -> Gold Kinesis -> Firehose -> S3 Gold
# 필요한 모든 리소스, 권한등 하나의 tf에서 구성
# variables
variable "gold_kinesis_shard_count" {
  description = "KDS's shard count"
  type        = number
  default     = 1
}
# kinesis 에서 미전송된 데이터 보관기간
variable "gold_kinesis_retention_hour" {
  description = "KDS's retention period in hours"
  type        = number
  default     = 24
}

# locals
locals {
    # Gold Kinesis 리소스 이름
    gold_kinesis_stream_name = "${var.project_name}-gold-kinesis"
    # Gold Firehose 리소스 이름
    gold_firehose_name  = "${var.project_name}-gold-firehose"
    # Silver 데이터 -> Gold용을 구성(집계등) 처리하는 lambda 함수명
    gold_lambda_name    = "${var.project_name}-silver-to-gold"
    # 람다 함수 배포용 zip 경로 (테라폼 업로드)
    gold_lambda_zip     = "${path.module}/../lambda/gold/gold-lambda.zip"
}

# kinesis
resource "aws_kinesis_stream" "gold" {
  name             = local.gold_kinesis_stream_name
  shard_count      = var.gold_kinesis_shard_count
  retention_period = var.gold_kinesis_retention_hour

  stream_mode_details {
    stream_mode = "PROVISIONED"
  }

  tags = {
    DataLayer = "gold"
    Purpose = "lambda-output"
  }
}

# IAM-ROLE

# Lambda

# Silver kinesis -> Lambda 연결

# Firehose IAM Role

# Gold Firehose












# 편의상 실시간성을 고려하여 구성
# silver -> lambda -> gold kinesis -> firehose 
#        -> Glue Schema -> Parquet(SNAPPY) -> s3 gold/

# 파이썬 파일 -> ZIP 패키징 관련
# lambda python 소스코드를 AWS lambda에 배포할 ZIP 파일에 포함하여 자동 생성
# data "archive_file" "gold_lambda" {
#     type        = "zip"
#     source_file = "${path.module}/../lambda/lambda_function.py"
#     output_path = "${path.module}/../lambda/gold-lambda.zip"
# }