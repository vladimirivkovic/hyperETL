import os
import sys
import traceback
import json

from collections import OrderedDict

from fabric_transformer.block_transformer import BlockTransformer as FabricBlockTransformer
from iroha_transformer.block_transformer import BlockTransformer as IrohaBlockTransformer

from connection.mongo import get_database
from loader.json2sql import init_db, clear_all, load_blocks, load_transactions, load_sc_args, load_operations

DB_NAME = "blockchain"
COL_NAME = "blocks"


def read_config():
    blockchain = os.environ["BLOCKCHAIN"]
    base_dir = os.environ["BASE_PATH"]
    return blockchain, base_dir


def load_transformed_json(blocks, drop=False):
    db = get_database(DB_NAME)

    if (drop):
        db[COL_NAME].drop()
        db.create_collection(COL_NAME)

    with open("schema/block_schema.json", "r") as j:
        block_schema = json.loads(j.read())

    cmd = OrderedDict([("collMod", COL_NAME),
                       ("validator", block_schema),
                       ("validationLevel", "moderate")]
                      )
    db.command(cmd)

    db[COL_NAME].insert_many(blocks)


def blocks_into_target_db():
    db = get_database(DB_NAME)
    col = db[COL_NAME]

    init_db()
    clear_all()

    try:
        blocks = col.find()
        load_blocks(blocks)
        blocks = col.find()
        load_transactions(blocks)
        blocks = col.find()
        load_sc_args(blocks)
        blocks = col.find()
        load_operations(blocks)
    except Exception as _:
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)
        del exc_info
        clear_all()


def main():
    BC_TYPE, BASE_DIR = read_config()
    print(BC_TYPE, BASE_DIR)

    blocks = []

    if BC_TYPE == "fabric":
        blocks = FabricBlockTransformer(BASE_DIR).blocks
    elif BC_TYPE == "iroha":
        blocks = IrohaBlockTransformer(BASE_DIR).blocks

    load_transformed_json(blocks, drop=True)
    blocks_into_target_db()


if __name__ == "__main__":
    main()
