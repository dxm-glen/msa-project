const serverless = require("serverless-http");

require('dotenv').config()

const express = require("express");
const app = express();
app.use(express.json())

const AWS = require("aws-sdk")
const sns = new AWS.SNS({ region: "ap-northeast-2" })


const {
  connectDb,
  queries: { getItems, getOneItem, setQuantity, getFactoryName }
} = require('./database')

app.get("/item", connectDb, async (req, res, next) => {
  const [result] = await req.conn.query(
    getItems()
  )
  console.log(`아이템 목록 : ${JSON.stringify(result)}`)
  await req.conn.end()
  if (result.length > 0) {
    return res.status(200).json(result);
  } else {
    return res.status(400).json({ message: "상품 없음" });
  }
});

app.post("/item", connectDb, async (req, res, next) => {
  const [result] = await req.conn.query(
    getOneItem(req.body.item_name)
  )

  if (result.length > 0) {
    const item = result[0]
    const [factory_data] = await req.conn.query(
      getFactoryName(item.factory_id)
    );
    const factory_name = factory_data[0].name;
    console.log(`아이템 정보 : ${JSON.stringify(item)}`);
    console.log(`공장이름 : ${factory_name}`);

    //남은 재고가 0또는 0이하가 될 경우 생산 진행
    if (item.quantity > 0 && item.quantity >= req.body.quantity) {
      await req.conn.query(setQuantity(item.item_id, item.quantity - req.body.quantity))
      return res.status(200).json({ message: `구매 완료! 남은 재고: ${item.quantity - req.body.quantity}` });
    }
    else {
      await req.conn.end()
      const now = new Date().toString()
      const message = `${item.name} 재고가 부족합니다. 제품을 생산해주세요! \n메시지 작성 시각: ${now}`
      const params = {
        Message: message,
        Subject: `${item.name} 재고 부족`,
        MessageAttributes: {
          MessageAttributeItemId: {
            StringValue: `${item.item_id}`,
            DataType: "Number",
          },
          MessageAttributeItemName: {
            StringValue: item.name,
            DataType: "String",
          },
          MessageAttributeFactoryId: {
            StringValue: `${item.factory_id}`,
            DataType: "Number",
          },
          MessageAttributeFactoryName: {
            StringValue: factory_name,
            DataType: "String",
          },
          MessageAttributeItemCnt: {
            StringValue: `${req.body.quantity}`,
            DataType: "Number",
          },
          MessageAttributeRequester: {
            StringValue: req.body.requester,
            DataType: "String",
          }
        },
        TopicArn: process.env.TOPIC_ARN
      }
      console.log("보내는 메시지 결과물  : ", params)
      await sns.publish(params).promise()
      return res.status(200).json({ message: `구매 실패! 남은 재고: ${item.quantity}, 생산요청 진행중` });
    }
  } else {
    await req.conn.end()
    return res.status(400).json({ message: "상품 없음" });
  }
});

app.put("/item/:id", connectDb, async (req, res, next) => {
  const item_id = req.params.id
  const quantity = req.body.quantity
  const [result] = await req.conn.query(
    setQuantity(item_id, quantity)
  )

  await req.conn.end()
  if (result) {
    return res.status(200).json({ message: "수량 변경 완료", result });
  } else {
    return res.status(400).json({ message: "수량 셋팅 실패" });
  }
});

app.use((req, res, next) => {
  return res.status(404).json({
    error: "Not Found",
  });
});

module.exports.handler = serverless(app);
module.exports.app = app;
