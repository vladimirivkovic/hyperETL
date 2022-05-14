DROP TABLE IF EXISTS key_history;
DROP TABLE IF EXISTS keys;
DROP TABLE IF EXISTS cc_args;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS blocks;

CREATE TABLE blocks (
    block_num INT PRIMARY KEY
);

CREATE TABLE transactions (
    tx_id VARCHAR(70) PRIMARY KEY,
    tx_timestamp TIMESTAMP,
    block_num INT NOT NULL,
    channel_id VARCHAR(128),
    chaincode_id VARCHAR(128),
    creator VARCHAR(128),
    endosments_no INT,
    response_msg VARCHAR(512),
    response_status INT,
    method VARCHAR(128),
    CONSTRAINT fk_block FOREIGN KEY (block_num) REFERENCES blocks(block_num)
);

CREATE TABLE cc_args (
    arg_id SERIAL,
    arg_number INT,
    arg_value VARCHAR(65536),
    tx_id VARCHAR(70),
    CONSTRAINT fk_tx FOREIGN KEY (tx_id) REFERENCES transactions(tx_id),
    CONSTRAINT pk_args UNIQUE (tx_id, arg_number)
);

CREATE TABLE keys (
    key_id VARCHAR(128) PRIMARY KEY,
    key_namespace VARCHAR(128) NOT NULL
);

CREATE TABLE key_history (
    key_id VARCHAR(128),
    tx_id VARCHAR(70),
    operation CHAR(1), -- R, W, Q
    payload VARCHAR(10024),
    is_delete BOOLEAN,
    version_ VARCHAR(128),
    CONSTRAINT fk_history1 FOREIGN KEY (tx_id) REFERENCES transactions(tx_id),
    CONSTRAINT fk_history2 FOREIGN KEY (key_id) REFERENCES keys(key_id),
    CONSTRAINT pk_history PRIMARY KEY (tx_id, key_id, operation)
);
