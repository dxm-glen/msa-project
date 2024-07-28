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
SELECT * FROM logs ORDER BY datetime DESC;
`

const recordLog = (factory_id, factory_name, item_id, item_name, quantity, requester, status) => `
INSERT INTO logs(factory_id, factory_name, item_id, item_name, quantity, requester, datetime, status) 
VALUES ('${factory_id}', '${factory_name}', '${item_id}', '${item_name}', '${quantity}', '${requester}', NOW(), '${status}');
`

const updateLogStatus = (id, status) => `
UPDATE logs SET status = '${status}' WHERE log_id = ${id};
`

// 기존의 deleteLog 함수는 유지합니다. 필요한 경우 사용할 수 있습니다.
const deleteLog = (id) => `
DELETE FROM logs WHERE log_id = ${id};
`

module.exports = {
    connectDb,
    queries: {
        getLog,
        recordLog,
        updateLogStatus,
        deleteLog
    }
}