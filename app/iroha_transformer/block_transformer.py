from util.logger import get_logger
from util.files import exists
from util.value_converter import timestamp_to_datetime
from iroha_transformer.transaction_transformer import TransactionTransformer


class BlockTransformer:
    def __init__(self, blocks_file_path: str) -> None:
        self.logger = get_logger(__name__)
        self.blocks_file_path = blocks_file_path
        self.metadata = {"metadata": {"blockchain": "iroha", "version": "",
                                      "source": self.blocks_file_path}}
        self.blocks = [
            {**(self.metadata), **(BlockTransformer.transform(raw_block))}
            for raw_block in self._extract_raw_blocks_from_txt_file()
        ]

    def _extract_raw_blocks_from_txt_file(self):
        filename = self.blocks_file_path

        if exists(filename) != 0:
            self.logger.warn("Blocks file dows not exist")
            return []

        with open(filename) as fin:
            blocks = fin.read().split("block ")

        return blocks[1:]

    @ staticmethod
    def transform(raw_block):
        return {
            "header": BlockTransformer.transform_header(raw_block),
            "transactions": [TransactionTransformer.transform(BlockTransformer.get_raw_transactions(raw_block))]
        }

    @ staticmethod
    def transform_header(raw_block):
        header = {
            "block_number": None,
            "block_hash": None,
            "previous_block_hash": None,
            "signer": None,
            "timestamp": None
        }

        lines = raw_block.strip().split("\n")
        for line in lines:
            no_ident = line.strip()
            if no_ident.startswith("height:"):
                header["block_number"] = int(
                    no_ident[(len("height:")+1):].strip())
            if no_ident.startswith("signature:"):
                header["block_hash"] = no_ident[(len("signature:")+1):].strip()
            if no_ident.startswith("prev_block_hash:"):
                header["previous_block_hash"] = no_ident[(
                    len("prev_block_hash:")+1):].strip()
            if no_ident.startswith("created_time:"):
                header["timestamp"] = timestamp_to_datetime(
                    no_ident[(len("created_time:")+1):].strip()[:-3])
            if no_ident.startswith("public_key:"):
                header["signer"] = no_ident[(len("public_key:")+1):].strip()

        print(header)
        return header

    def get_raw_transactions(raw_block):
        transactions_entered = False
        transactions_lines = []
        lines = raw_block.strip().split("\n")

        for line in lines:
            no_ident = line.strip()

            if no_ident == "transactions {":
                open = 0
                closed = 0
                transactions_entered = True

            if transactions_entered:
                if "{" in line:
                    open += 1
                if "}" in line:
                    closed += 1
                if closed == open:
                    transactions_entered = False

                transactions_lines.append(line)

        return transactions_lines
