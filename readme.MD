# 목표
- AWS Fargate를 이용한 로그 생성기
  - AWS Fargate
    - EC2 사용/관리 x
    - ECR에 등록된 이미지를 이용하여 ECS에서 직접 컨테이너 실행 -> `서버리스`로 실행환경 제공 받고 수행 
    - 비용 가장 저렴
  - 발생된 데이터
    - 데이터 형태 : 요청 -> 서비스 대응 -> 응답 => 모두 합친 최종 로그, 서비스 구성 x
    - 데이터 저장 
      - s3 : 다음 챕터에서 확장 활용
      - cloudwatch : aws 로그 저장
      - file
      - 콘솔

# 인프라 구성
- variables.tf
- version.tf
- provider.tf
- locals.tf
- vpc.tf
- iam.tf
- logs.tf
- ecr.tf
- esc.tf
- outputs.tf