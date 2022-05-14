import os
import json

from model.block import Block
from util.logger import get_logger


class BlockExtractor:
    def __init__(self, base_dir: str, prefix=""):
        self.logger = get_logger(__name__)
        self.base_dir = base_dir
        self.prefix = prefix
        self.blocks = self._extract_from_base_dir()

    def _extract_from_base_dir(self):
        blocks = []
        i = 0

        while True:
            filename = f"{self.base_dir}/{self.prefix}{i}.json"
            if BlockExtractor._file_exists(filename) != 0:
                break
            blocks.append(self._extract_block(filename))
            i += 1

        if i > 0:
            self.logger.info(f"{i} blocks read")
        else:
            self.logger.warn("No blocks found")

        return blocks

    def _extract_block(self, filename):
        with open(filename, encoding="utf8") as f:
            block_raw = json.load(f)
            return Block(block_raw["header"], block_raw["data"]["data"])

    @staticmethod
    def _file_exists(fn):
        cmd = f"stat {fn} >/dev/null 2>&1" # Linux
        # cmd = f"stat {fn} >nul 2>&1"
        return os.system(cmd)
