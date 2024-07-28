const axios = require('axios').default;
require('dotenv').config();

const consumer = async (event) => {
  const processedRecords = [];

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
        "callback_url": process.env.CALLBACK_URL
      };
      
      console.log(`payload : ${JSON.stringify(payload)}`);
      console.log(`현재 등록된 공장 시스템 주소(factory lambda url) : ${process.env.FACTORY_URL}`);
      
      try {
        const response = await axios.post(
          `${process.env.FACTORY_URL}/log`,
          payload,
          { timeout: 60000 } // 60초 타임아웃 설정
        );
        
        console.log(`공장에서 온 응답 : ${JSON.stringify(response.data)}`);
        processedRecords.push({ id: record.messageId, success: true });
      } catch (axiosError) {
        if (axiosError.code === 'ECONNABORTED') {
          throw new Error(`공장 요청 타임아웃: ${process.env.FACTORY_URL}`);
        } else if (axiosError.code === 'ENOTFOUND' || axiosError.code === 'ECONNREFUSED') {
          throw new Error(`공장 URL을 찾을 수 없음: ${process.env.FACTORY_URL}`);
        } else if (axiosError.response) {
          // 서버에서 응답은 왔지만 2xx 범위를 벗어나는 상태 코드인 경우
          throw new Error(`공장에서 오류 응답: ${axiosError.response.status} - ${axiosError.response.data}`);
        } else if (axiosError.request) {
          // 요청은 보냈지만 응답을 받지 못한 경우
          throw new Error(`공장으로부터 응답 없음: ${process.env.FACTORY_URL}`);
        } else {
          // 요청 설정 중 오류가 발생한 경우
          throw new Error(`요청 설정 중 오류 발생: ${axiosError.message}`);
        }
      }
    } catch (error) {
      console.error(`처리 중 오류 발생: ${error.message}`);
      processedRecords.push({ id: record.messageId, success: false, error: error.message });
    }
  }

  const failedRecords = processedRecords.filter(record => !record.success);

  if (failedRecords.length > 0) {
    const errorMessages = failedRecords.map(record => `메시지 ID ${record.id}: ${record.error}`).join('\n');
    throw new Error(`메시지 처리 실패:\n${errorMessages}`);
  }

  return {
    statusCode: 200,
    body: JSON.stringify({ message: '모든 메시지 처리 성공' })
  };
};

module.exports = {
  consumer,
};