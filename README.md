# STEP 1 : 환경설정
- Cloud9 환경에 코드 확보
    - `git clone https://github.com/dxm-glen/msa-project.git`
- 서버리스 설치
    - `npm install serverless -g`

# STEP 2 : Shop-api 구성하기
- 상품 조회, 수정, 구매 서버 역할을 하는 람다
- 경로 이동
    - `cd ~/environment/msa-project/shop-api`
- 환경설정 파일 구성
    - .env 파일 생성
    ```
     HOSTNAME= 샵 데이터베이스 엔드포인트
     USERNAME=DB_000
     PASSWORD=000000
     DATABASE=DB_000
    ```
- 디펜던시 설치
    - `npm install`
- 함수 이름 설정
    - serverless.yml 에서 service 이름 자신의 번호로 수정
- 함수 배포
    - `sls deploy`
- 포스트맨에서 함수 조회 / 수정 테스트
    - 상품 조회
        - get
        - 함수url/item
    - 상품 수정
        - put
        - 함수url/item/:id
            ```
            {
                "quantity" : 5
            }
            ```
- 포스트맨에서 구매 테스트
    - 상품 구매
        - post
        - 함수 url/item
            ```
            {
                "item_name": "Item3",
                "quantity": 1,
                "requester": "tester"
            }
            ```
    - 수량 0에서 구매 요청할 경우 SNS 오류 발생
        - CloudWatch 확인
            - `"InvalidParameter: Invalid parameter: TopicArn or TargetArn Reason: no value for required parameter"`

# STEP 3 : SNS, SQS 구성
- AWS Console에서 SNS 생성
    - msa-000-empty-topic
    - 표준
- AWS Console에서 SQS 생성
    - msa-000-sqs
    - 표준
    - SNS(msa-000-empty-topic) 구독 연결 
- shop-api .env에 SNS ARN 추가
    - `TOPIC_ARN=생성한 SNS ARN `
    - .env 수정후 재배포
        -`sls deploy` 
- 포스트맨에서 구매 테스트 재시도
    - 권한오류 발생
    - `no identity-based policy allows the SNS:Publish action`
# STEP 4 : 권한 오류 수정
    - Lambda가 SNS에 접근할 수 있는 역할 수정
    - 람다 -> 권한 -> IAM Role 접근
    - 인라인 정책 추가
    -  SNS, publish, sns_arn 연결
    -  포스트맨에서 구매 재시도
        ```
            {
               "message": "구매 실패! 남은 재고: 0, 생산요청 진행중"
            }
        ```
    - sqs에서 메시지 폴링으로 확인
        ```
            {
              "Type" : "Notification",
              "MessageId" : "SAMPLE",
              "TopicArn" : "SAMPLE",
              "Subject" : "Item3 재고 부족",
              "Message" : "Item3 재고가 부족합니다. 제품을 생산해주세요! \n메시지 작성 시각: Mon May 13 2024 08:59:40 GMT+0000 (Coordinated Universal Time)",
              "Timestamp" : "SAMPLE",
              "SignatureVersion" : "1",
              "Signature" : "SAMPLE",
              "SigningCertURL" : "SAMPLE",
              "UnsubscribeURL" : "SAMPLE",
              "MessageAttributes" : {
                "MessageAttributeRequester" : {"Type":"String","Value":"tester"},
                "MessageAttributeItemCnt" : {"Type":"Number","Value":"1"},
                "MessageAttributeFactoryId" : {"Type":"Number","Value":"1"},
                "MessageAttributeFactoryName" : {"Type":"String","Value":"Factory1"},
                "MessageAttributeItemId" : {"Type":"Number","Value":"3"},
                "MessageAttributeItemName" : {"Type":"String","Value":"Item3"}
              }
            }
        ```
# STEP 5 : order-lambda 구성
- SQS에서 메시지를 받아와서 공장에 전달하는 람다
- 경로이동
    - `cd ~/environment/msa-project/order-lambda`
- 디펜던시 설치
    - `npm install`
- 함수 설정
    - serverless.yml 에서 service 이름 자신의 번호로 수정
    - SQS에 sqs arn을 문자열로 입력
    - 플러그인 설치
        - `serverless plugin install -n serverless-lift`
- 함수 배포
    - `sls deploy`
- 생성후 SQS에서 메시지 사라진것을 확인
- CloudWatch 로그 확인
    - FACTORY_URL이 없어서 전송 실패

# STEP 6 : Factory-api 구성
- 생산 요청을 받아서 생산 로그를 기록하고 일정 시간이 지나면 생산 완료를 보내는 공장 서버 람다
- 경로이동
    - `cd ~/environment/msa-project/factory-api`
- 환경설정 파일 구성
    - .env 파일 생성
    ```
     HOSTNAME=팩토리 데이터베이스 엔드포인트
     USERNAME=DB_000
     PASSWORD=000000
     DATABASE=DB_000
    ```
- 디펜던시 설치
    - `npm install`
- 함수 설정
    - serverless.yml 에서 service 이름 자신의 번호로 수정
- 함수 배포
    - `sls deploy`  
- order-lambda 환경변수설정
    - .env 파일 생성
    - `FACTORY_URL= Factory-api 람다의 URL/log`
        - 람다 주소 뒤에 `/log` 붙여야함
    - order-lambda 재배포
        - `sls deploy` 
- 생산 요청 로그 확인
    - `GET factory-lambda url/log`
    -  예시
        ```
            [
                {
                    "log_id": 1,
                    "factory_id": 1,
                    "factory_name": "Factory1",
                    "item_id": 1,
                    "item_name": "Item1",
                    "quantity": 5,
                    "requester": "jeonghun",
                    "datetime": "2024-05-13T06:05:12.000Z"
                },
                {
                    "log_id": 2,
                    "factory_id": 1,
                    "factory_name": "Factory1",
                    "item_id": 3,
                    "item_name": "Item3",
                    "quantity": 4,
                    "requester": "tester",
                    "datetime": "2024-05-13T09:44:46.000Z"
                },
                {
                    "log_id": 3,
                    "factory_id": 1,
                    "factory_name": "Factory1",
                    "item_id": 3,
                    "item_name": "Item3",
                    "quantity": 4,
                    "requester": "tester",
                    "datetime": "2024-05-13T09:45:16.000Z"
                }
            ]
        ```
- factory-api 람다 로그 확인
    - 에러발생 `ERROR	Error sending callback: ReferenceError: axios is not defined `
    - 생산 수량을 데이터베이스에 기록할 람다에 전달해야함
# STEP 7 : Delivery-lambda 구성
- 공장이 생산 완료 후 생산한 물품 수량을 데이터베이스에 기록할 람다
- 경로이동
    - `cd ~/environment/msa-project/delivery-lambda`
- 환경설정 파일 구성
    - .env 파일 생성
    ```
     HOSTNAME=샵 데이터베이스 엔드포인트
     USERNAME=DB_000
     PASSWORD=000000
     DATABASE=DB_000
    ```
- 디펜던시 설치
    - `npm install`
- 함수 설정
    - serverless.yml 에서 service 이름 자신의 번호로 수정
- 함수 배포
    - `sls deploy`
- factory-api .env에 생성된 delivery-lambda url 추가
    - CALLBACKURL=람다 URL
    - 재배포 실행
        - factory-api 경로에서 `sls deploy`
- 구매 테스트
    - delivery-lambda 로그 확인 
    - `배송완료 - item_id : 3, quantity: 2`