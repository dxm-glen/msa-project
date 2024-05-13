const axios = require('axios').default
require('dotenv').config()

const consumer = async (event) => {
  for (const record of event.Records) {
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
      "factory_name": factory_name
    }
    console.log(`payload : ${JSON.stringify(payload)}`);
    console.log(`factory lambda url : ${process.env.FACTORY_URL}`);
    try {
      const response = await axios.post(
        `${process.env.FACTORY_URL}`,
        payload
      );
      console.log(`공장에서 온 응답 : ${JSON.stringify(response.data)}`);
    } catch (error) {
      console.error(error);
    }
  }
};

module.exports = {
  consumer,
};
