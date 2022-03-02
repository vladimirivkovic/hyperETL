
import os
import sys
import traceback
import configparser

from extractor.block_extractor import BlockExtractor
from extractor.transaction_extractor import TransactionExtractor
from extractor.key_extractor import KeyExtractor

from etl.loader import load_blocks, load_transactions, load_cc_args, load_keys, load_key_history, clear_all, init_db


def read_config():
    config = configparser.ConfigParser()
    config.read(os.environ["CONFIG_PATH"])
    return config["DEFAULT"]["BASE_DIR"]


def extract_data(base_dir: str):
    blocks = BlockExtractor(base_dir).blocks
    txs = []
    for block in blocks:
        txs += TransactionExtractor(block).transactions

    return blocks, txs


def etl(blocks, txs):
    init_db()
    clear_all()
    try:
        load_blocks(blocks)
        load_transactions(txs)
        load_cc_args(txs)

        keys = KeyExtractor.process_transactions(txs).values()
        load_keys(keys)
        load_key_history(keys)
    except Exception as _:
        exc_info = sys.exc_info()
        traceback.print_exception(*exc_info)
        del exc_info
        clear_all()


def main():
    BASE_DIR = read_config()

    blocks, txs = extract_data(BASE_DIR)

    etl(blocks, txs)


if __name__ == "__main__":
    main()
