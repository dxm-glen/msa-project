# msa-project



# SHOP-API-LAMBDA

`npm install serverless -g`

.env 생성

```
HOSTNAME=데이터베이스 엔드포인트
USERNAME=DB_000
PASSWORD=000000
DATABASE=DB_000
```

yaml 설정

- service 이름 변경

sls deploy

# 포스트맨 사용

- GET

  - /item
- POST

  - /item
    - ```
      {
          "item_name": "Item2",
          "quantity": 1,
          "requester": "tester"
      }
      ```
- PUT

  - /item/:id
  - ```
    {
        "quantity" : 5
    }
    ```



# SNS

- msa-000-empty-topic 생성
- .env에 TOPIC_ARN 입력

# SQS

- SNS 구독 연결

# 권한 에러 확인

- no identity-based policy allows the SNS:Publish action
- IAM 인라인 정책 추가
- sns, publish, ARN 입력
- 구매 재시도

  - 성공시 메시지 : "message":"구매 실패! 남은 재고: 0, 생산요청 진행중"
- SQS에서 메시지 확인
