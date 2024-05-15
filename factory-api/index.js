const axios = require('axios').default
const serverless = require("serverless-http");
require('dotenv').config()
const express = require("express");

const app = express();
app.use(express.json());

const {
  connectDb,
  queries: { getLog, recordLog }
} = require('./database')

app.get("/log", connectDb, async (req, res, next) => {
  const result = await req.conn.query(
    getLog()
  )
  await req.conn.end()
  if (result.length > 0) {
    return res.status(200).json(result[0]);
  } else {
    return res.status(400).json({ message: "기록 없음" });
  }
}
);

app.post("/log", connectDb, async (req, res, next) => {
  console.log(`받은 데이터 :  ${JSON.stringify(req.body)}`);
  const { requester, quantity, item_id, item_name, factory_id, factory_name, callback_url } = req.body;

  console.log("생산 시작합니다.")
  console.log("생산 품목: ", item_id, item_name)
  console.log("생산 공장: ", factory_id, factory_name)
  console.log("생산 수량: ", quantity)
  console.log("생산 요청자: ", requester)
  console.log("생산 완료 후 item db quantity 증가 람다 주소 : ", callback_url)

  await req.conn.query(
    recordLog(factory_id, factory_name, item_id, item_name, quantity * 2, requester)
  );
  await req.conn.end();
  console.log("데이터베이스에 생산요청 기록 완료");

  setTimeout(async () => {
    try {
      const response = await axios.post(callbackUrl, req.body);
    } catch (error) {
      console.error('Error sending callback:', error);
    }
  }, 10000);

  return res.status(200).json({ message: `상품 : ${item_id, item_name} \n 수량 : ${quantity}, 데이터베이스 수량 증가 기록 요청중` });
}
);

module.exports.handler = serverless(app);



