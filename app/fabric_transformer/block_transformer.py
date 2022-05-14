import json

from fabric_transformer.transaction_transformer import TransactionTransformer
from util.logger import get_logger
from util.files import exists


class BlockTransformer:
    def __init__(self, base_dir: str, prefix="") -> None:
        self.logger = get_logger(__name__)
        self.base_dir = base_dir
        self.prefix = prefix
        self.metadata = {"metadata": {"blockchain": "fabric", "version": "1.4.7",
                                 "source": self.base_dir}}
        self.blocks = [
            {**(self.metadata), **(BlockTransformer.transform(raw_block))} 
            for raw_block in self._extract_raw_blocks_from_base_dir()
        ]

    def _extract_raw_blocks_from_base_dir(self):
        blocks = []
        i = 0

        while True:
            filename = f"{self.base_dir}/{self.prefix}{i}.json"
            if exists(filename) != 0:
                break
            blocks.append(self._extract_raw_block(filename))
            i += 1

        if i > 0:
            self.logger.info(f"{i} blocks read")
        else:
            self.logger.warn("No blocks found")

        return blocks

    def _extract_raw_block(self, filename):
        with open(filename, encoding="utf8") as f:
            return json.load(f)

    @ staticmethod
    def transform_header(raw_block):
        return {
            "block_number": int(raw_block["header"]["number"]),
            "block_hash": raw_block["header"]["data_hash"],
            "previous_block_hash": raw_block["header"]["previous_hash"],
            "signer": raw_block["metadata"]["metadata"][0],
            "timestamp": None                                       # TODO: find
        }

    @ staticmethod
    def transform(raw_block):
        return {
            "header": BlockTransformer.transform_header(raw_block),
            "transactions": TransactionTransformer.transform(raw_block["data"]["data"])
        }
