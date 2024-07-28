const axios = require('axios').default;
const serverless = require("serverless-http");
require('dotenv').config();
const express = require("express");
const app = express();
app.use(express.json());
const {
  connectDb,
  queries: { getLog, recordLog, updateLogStatus }
} = require('./database');

// Helper function to create a delay
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

app.get("/log", connectDb, async (req, res, next) => {
  const result = await req.conn.query(getLog());
  await req.conn.end();
  if (result.length > 0) {
    return res.status(200).json(result[0]);
  } else {
    return res.status(400).json({ message: "기록 없음" });
  }
});

app.post("/log", connectDb, async (req, res, next) => {
  console.log(`받은 데이터 :  ${JSON.stringify(req.body)}`);
  const { requester, quantity, item_id, item_name, factory_id, factory_name, callback_url } = req.body;
  console.log("생산 시작합니다.");
  console.log("생산 품목: ", item_id, item_name);
  console.log("생산 공장: ", factory_id, factory_name);
  console.log("생산 수량: ", quantity);
  console.log("생산 요청자: ", requester);
  console.log("생산 완료 후 item db quantity 증가 람다 주소 : ", callback_url);
  
  // 최초 로그 기록 (상태: 대기중)
  const [result] = await req.conn.query(recordLog(factory_id, factory_name, item_id, item_name, quantity, requester, '대기중'));
  const recordId = result.insertId;
  console.log("데이터베이스에 생산요청 기록 완료, ID:", recordId);

  console.log("생산 완료까지 30초...")
  await delay(10000);
  console.log("생산 완료까지 20초...")
  await delay(10000);
  console.log("생산 완료까지 10초...")
  await delay(10000);
  console.log("생산 완료");
  
  try {
    // Send callback after production
    const response = await axios.post(callback_url, req.body);
    console.log("callback URL로 POST 요청 성공:", response.data);
    
    // 성공 시 로그 상태 업데이트
    await req.conn.query(updateLogStatus(recordId, '성공'));
    console.log("로그 상태 업데이트 완료: 성공");

    res.status(200).json({
      message: `상품: ${item_id}, ${item_name} \n 수량: ${quantity}, 대상: ${callback_url} \n 생산 완료 후 배송 -> 생산완료 정보를 시스템에 전달(${callback_url})`
    });
  } catch (error) {
    console.error("callback URL로 POST 요청 실패:", error.message);
    
    // 실패 시 로그 상태 업데이트
    await req.conn.query(updateLogStatus(recordId, '실패'));
    console.log("로그 상태 업데이트 완료: 실패");

    res.status(400).json({
      message: `상품: ${item_id}, ${item_name} \n 수량: ${quantity}, 대상: ${callback_url} \n 생산완료 정보를 전달할 시스템(${callback_url}) 오류 확인 -> 생산 중단`
    });
  } finally {
    await req.conn.end();
  }
});

module.exports.handler = serverless(app);