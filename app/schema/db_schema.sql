DROP TABLE IF EXISTS operations;
DROP TABLE IF EXISTS sc_args;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS blocks;

CREATE TABLE blocks (
    block_id SERIAL PRIMARY KEY,
    block_num INT,
    block_hash VARCHAR(512),
    previous_block_hash VARCHAR(512),
    block_timestamp TIMESTAMP,
    signature TEXT,
    blockchain_type VARCHAR(32),
    blockchain_version VARCHAR(32),
    blockchain_source VARCHAR(512)
);

CREATE TABLE transactions (
    transaction_id SERIAL PRIMARY KEY,
    transaction_hash VARCHAR(512),
    transaction_timestamp TIMESTAMP,
    block_id INT NOT NULL,
    smart_contract VARCHAR(128),
    creator VARCHAR(128),
    response VARCHAR(512),
    status INT,
    method VARCHAR(128),
    CONSTRAINT fk_block FOREIGN KEY (block_id) REFERENCES blocks(block_id)
);

CREATE TABLE sc_args (
    arg_id SERIAL PRIMARY KEY,
    arg_number INT,
    arg_value VARCHAR(65536),
    transaction_id INT,
    CONSTRAINT fk_tx FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
    CONSTRAINT uq_args UNIQUE (transaction_id, arg_number)
);

CREATE TABLE operations (
    operation_id SERIAL PRIMARY KEY,
    key_id VARCHAR(128),
    transaction_id INT,
    operation_type CHAR(1), -- R, W, Q
    payload TEXT,
    is_delete BOOLEAN,
    version_ VARCHAR(128),
    -- CONSTRAINT uq_operations UNIQUE (transaction_id, key_id, operation_type),
    CONSTRAINT fk_operations FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id)
);
