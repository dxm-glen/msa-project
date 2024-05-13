const mysql = require('mysql2/promise');
require('dotenv').config()

const {
  HOSTNAME: host,
  USERNAME: user,
  PASSWORD: password,
  DATABASE: database
} = process.env;

const consumer = async (event) => {
  for (const record of event.Records) {
    const json = JSON.parse(record.body)
    console.log(`도착 데이터 : ${JSON.stringify(json)}`);

    const quantity = Number(json.MessageAttributeItemCnt.Value);
    const item_id = Number(json.MessageAttributeItemId.Value);
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
  }
};

module.exports = {
  consumer,
};
