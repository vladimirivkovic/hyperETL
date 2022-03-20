
import os
import configparser
import json

from collections import OrderedDict

from fabric_transformer.block_transformer import BlockTransformer as FabricBlockTransformer
from iroha_transformer.block_transformer import BlockTransformer as IrohaBlockTransformer

from connection.mongo import get_database

DB_NAME = "blockchain"
COL_NAME = "blocks"


def read_config():
    config = configparser.ConfigParser()
    config.read(os.environ["CONFIG_PATH"])
    return config["DEFAULT"]["BASE_DIR"]


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


def main():
    BASE_DIR = read_config()

    blocks = FabricBlockTransformer(BASE_DIR).blocks
    # print(json.dumps(blocks[5], indent=2))

    # blocks = IrohaBlockTransformer("/tmp/iroha/blocks/blocks.txt").blocks
    # print(json.dumps(blocks[0], indent=2))
    load_transformed_json(blocks, drop=True)


if __name__ == "__main__":
    main()
