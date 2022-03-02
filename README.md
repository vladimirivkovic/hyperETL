# hyperETL
## ETL solution for Hyperledger Blockchain data

### Prereqs
- Docker & Docker-compose
- Python

### Prepare blockchain data
Steps:
- clone a Blockchain-Insurance-App repository
- in Blockchain-Insurance-App repository: run `./build_ubuntu.sh` script
- in this repository: run `python3 scenario.py` from `samples/insurance-app` directory
- wait until scenario is finished
- in Blockchain-Insurance-App repository, from `blocks/blocks` copy all block files to `samples/insurance-app/blocks`
- in Blockchain-Insurance-App repository, stop blockchain with `./clean.sh`

### Run HyperETL and visualize results
Steps:
- run `docker-compose up`
- open Metabase web UI on [localhost:3000](http://localhost:3000)
- log in to Metabase
- connect to Postgres database
- execute queries and visualize results ([Getting Started with Metabase](https://www.metabase.com/learn/getting-started/getting-started.html))