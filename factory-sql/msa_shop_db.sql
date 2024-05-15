-- factories 테이블
CREATE TABLE factories (
    factory_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    locate VARCHAR(255)
);

-- itmes 테이블
CREATE TABLE items (
    item_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255),
    price INT,
    quantity INT,
    factory_id INT,
    FOREIGN KEY (factory_id) REFERENCES factories(factory_id)
);

-- 샘플 데이터 입력
INSERT INTO factories (name, locate)
VALUES
    ('Factory1', 'korea'),
    ('Factory2', 'usa');
    
INSERT INTO items (name, price, quantity, factory_id)
VALUES
    ('Item1', 10000, 1, 1),
    ('Item2', 20000, 2, 2),
    ('Item3', 30000, 3, 1);

