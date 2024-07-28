const axios = require('axios').default
require('dotenv').config()

const consumer = async (event) => {
  for (const record of event.Records) {
    try {
      const json = JSON.parse(record.body).MessageAttributes;
      console.log(`도착 데이터 : ${JSON.stringify(json)}`);
      const requester = json.MessageAttributeRequester.Value;
      const quantity = Number(json.MessageAttributeItemCnt.Value) * 2;
      const item_id = Number(json.MessageAttributeItemId.Value);
      const item_name = json.MessageAttributeItemName.Value;
      const factory_id = Number(json.MessageAttributeFactoryId.Value);
      const factory_name = json.MessageAttributeFactoryName.Value;
      const payload = {
        "requester": requester,
        "quantity": quantity,
        "item_id": item_id,
        "item_name": item_name,
        "factory_id": factory_id,
        "factory_name": factory_name,
        "callback_url": "Delivery-lambda의 URL"
      }
      console.log(`payload : ${JSON.stringify(payload)}`);
      console.log(`factory lambda url : ${process.env.FACTORY_URL}`);
      
      const response = await axios.post(
        `${process.env.FACTORY_URL}`,
        payload,
        { timeout: 5000 } // 5초 타임아웃 설정
      );
      console.log(`공장에서 온 응답 : ${JSON.stringify(response.data)}`);
    } catch (error) {
      console.error(`처리 중 오류 발생: ${error.message}`);
      throw new Error('메시지 처리 실패'); // 에러를 던져 Lambda 실행을 실패로 표시
    }
  }
};

module.exports = {
  consumer,
};