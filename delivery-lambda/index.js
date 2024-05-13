const mysql = require('mysql2/promise');
require('dotenv').config()

const {
  HOSTNAME: host,
  USERNAME: user,
  PASSWORD: password,
  DATABASE: database
} = process.env;

const consumer = async (event) => {
  console.log(`도착 데이터 : ${event.body}`);
  let json;
  try {
    json = JSON.parse(event.body);
  } catch (error) {
    console.error('JSON parsing error:', error);
    return;
  }
  const quantity=json.quantity
  const item_id=json.item_id
  console.log(`quantity : ${quantity}`)
  console.log(`item_id: ${item_id}`)
  try {
      const connect = await mysql.createConnection({ host, user, password, database });
      const [quantity_in_db] = await connect.query(`SELECT quantity from items WHERE item_id = ${item_id};`);
      const quantity_before = quantity_in_db[0].quantity;
      const total_quantity = quantity + quantity_before;
      await connect.query(`UPDATE items SET quantity = ${total_quantity} WHERE item_id = ${item_id};`);
      console.log(`배송완료 - item_id : ${item_id}, quantity: ${total_quantity}`);
      connect.end();
    } catch (e) {
      console.log(`데이터베이스 연결 오류 : ${e}`);
    }
};

module.exports = {
  consumer,
};
