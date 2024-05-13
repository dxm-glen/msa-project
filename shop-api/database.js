const mysql = require('mysql2/promise');
require('dotenv').config()

const {
  HOSTNAME: host,
  USERNAME: user,
  PASSWORD: password,
  DATABASE: database
} = process.env;

const connectDb = async (req, res, next) => {
  try {
    req.conn = await mysql.createConnection({ host, user, password, database })
    next()
  }
  catch (e) {
    console.log(e)
    res.status(500).json({ message: "데이터베이스 연결 오류" })
  }
}

const getItems = () => `
  SELECT *
  FROM items;
`

const getOneItem = (item_name) => `
  SELECT *
  FROM items
  WHERE name = '${item_name}';
`

const setQuantity = (item_id, quantity) => `
  UPDATE items SET quantity = ${quantity} WHERE item_id = ${item_id};
`

const getFactoryName = (factory_id) => `
  SELECT name
  FROM factories 
  WHERE factory_id = '${factory_id}';
`

module.exports = {
  connectDb,
  queries: {
    getItems,
    getOneItem,
    setQuantity,
    getFactoryName
  }
}