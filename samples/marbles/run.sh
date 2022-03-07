docker network create iroha-network

docker run --name some-postgres \
-e POSTGRES_USER=postgres \
-e POSTGRES_PASSWORD=mysecretpassword \
-p 5432:5432 \
--network=iroha-network \
-d postgres:9.5 \
-c 'max_prepared_transactions=100'

docker volume create blockstore

git clone https://github.com/hyperledger/iroha --depth=1

docker run --name iroha \
-d \
-p 50051:50051 \
-v $(pwd)/iroha/example:/opt/iroha_data \
-v blockstore:/tmp/block_store \
--network=iroha-network \
-e KEY='node0' \
hyperledger/iroha:latest

docker exec -it iroha /bin/bash

### Iroha python client
apt update
apt -y install python3-pip 
pip3 install iroha

python3 infinite-blocks-stream.py # listening for new blocks
### new terminal
# python3 tx-example.py
docker exec -it iroha /bin/bash -c "python3 python/tx-example.py"

# OR 
python3 block-query.py > blocks.txt # retrieving all existing blocks

### Iroha-CLI
iroha-cli -account_name admin@test

### shutdown
docker stop iroha
docker stop some-postgres
docker rm iroha
docker rm some-postgres
docker volume rm blockstore

