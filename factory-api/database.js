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
const getLog = () => `
SELECT * FROM logs;
`

const recordLog = (factory_id, factory_name, item_id, item_name, quantity, requester) => `
INSERT INTO logs(factory_id, factory_name, item_id, item_name, quantity, requester, datetime) VALUES ('${factory_id}', '${factory_name}', '${item_id}', '${item_name}', '${quantity}', '${requester}', NOW());
`

module.exports = {
    connectDb,
    queries: {
        getLog,
        recordLog
    }
}