const mysql = require('mysql2/promise');
require('dotenv').config();

const {
  HOSTNAME: host,
  USERNAME: user,
  PASSWORD: password,
  DATABASE: database
} = process.env;

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

const consumer = async (event) => {
  console.log(`도착 데이터 : ${event.body}`);
  let json;
  try {
    json = JSON.parse(event.body);
  } catch (error) {
    console.error('JSON parsing error:', error);
    return;
  }
  console.log("#####################################")
  console.log("json 파싱된 body 데이터 확인")
  console.log(json)
  console.log("#####################################")
  
  const quantity = json.quantity;
  const item_id = json.item_id;
  console.log(`quantity : ${quantity}`);
  console.log(`item_id: ${item_id}`);

  try {
    await delay(5000); // 5초 대기
    console.log("공장에서 받아온 물건 하역중..")
    await delay(5000); // 5초 대기
    console.log("물건 목록 확인중..")
    await delay(5000); // 5초 대기
    console.log("물건 수량 확인중..")
    await delay(5000); // 5초 대기
    console.log("창고에 물건 적재중..")
    await delay(5000); // 5초 대기
    console.log("적재 내용 데이터베이스에 등록중..")

    // 데이터베이스에 연결
    const connect = await mysql.createConnection({ host, user, password, database });
    
    // 현재 재고사항 파악
    const [quantity_in_db] = await connect.query(`SELECT quantity from items WHERE item_id = ${item_id};`);
    const quantity_before = quantity_in_db[0].quantity;
    
    // 기존 재고 + 생산물품 수량 확인
    const total_quantity = quantity + quantity_before;
    
    // 데이터베이스의 items 테에블에서, 생산된 물품(item_id)에 수량 정보(quantity) 수정 쿼리 작성하기
    // const query=`여기에 적절 한 쿼리문을 작성하세요.`
    const query=`UPDATE items SET quantity = ${total_quantity} WHERE item_id = ${item_id};`
    
    
    await connect.query(query);
    console.log(`배송완료 - item_id : ${item_id}, quantity: ${total_quantity}`);
    await connect.end();
    
    
  } catch (e) {
    console.log(`데이터베이스 연결 오류 : ${e}`);
  }
};

module.exports = {
  consumer,
};
