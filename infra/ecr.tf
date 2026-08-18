# 로그 생성기가 구동되는 컨테이너의 이미지가 저장되는 저장소
# 1. 저장소 생성
resource "aws_ecr_repository" "generator" {
  
}

# 2. 저장소 저장 비용 관리 정책 결정 -> 오래된 이미지를 언제까지 보관할 것인가
resource "aws_ecr_lifecycle_policy" "generator" {
  
}