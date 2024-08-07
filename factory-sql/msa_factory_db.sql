-- logs 테이블
CREATE TABLE logs (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    factory_id INT,
    factory_name VARCHAR(255),
    item_id INT,
    item_name VARCHAR(255),
    quantity INT,
    requester VARCHAR(255),
    datetime DATETIME,
    status ENUM('대기중', '성공', '실패') NOT NULL
);

-- 샘플 데이터 입력
INSERT INTO logs (factory_id, factory_name, item_id, item_name, quantity, requester, datetime, status)
VALUES (1, 'Factory1', 1, 'Item1', 5, 'jeonghun', NOW(), '성공');