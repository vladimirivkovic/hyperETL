import jmespath

from util.logger import get_logger
from util.decoder import decode


class TransactionTransformer:
    def __init__(self) -> None:
        self.logger = get_logger(__name__)

    @staticmethod
    def transform(raw_transactions):
        return {
            "header": TransactionTransformer.transform_header(raw_transactions),
            "data": [TransactionTransformer.transform_command(command) for command in TransactionTransformer.get_commands(raw_transactions)]
        }

    @staticmethod
    def transform_header(raw_transactions):
        header = {
            "transaction_id": None,
            "smart_contract": None,
            "creator": None,
            "timestamp": None
        }

        for line in raw_transactions:
            no_ident = line.strip()
            if no_ident.startswith("signature:"):
                header["transaction_id"] = no_ident[(
                    len("signature:")+1):].strip()
            if no_ident.startswith("creator_account_id:"):
                header["creator"] = no_ident[(
                    len("creator_account_id:")+1):].strip()
            if no_ident.startswith("created_time:"):
                header["timestamp"] = no_ident[(
                    len("created_time:")+1):].strip()

        return header

    @staticmethod
    def get_commands(raw_transactions):
        commands_entered = False
        commands = []
        command = {"method": None, "args": []}

        for line in raw_transactions:
            no_ident = line.strip()

            if no_ident == "commands {":
                open = 0
                closed = 0
                commands_entered = True
                command = {"method": None, "args": []}

            if commands_entered:
                if "{" in line:
                    open += 1
                if "}" in line:
                    closed += 1
                if closed == open:
                    commands_entered = False
                    commands.append(command)

                if "{" in line:
                    command["method"] = line.split("{")[0].strip()
                if ":" in line:
                    words = line.split(":")
                    command["args"].append(
                        (words[0].strip(), words[1].strip()))

        return commands

    @staticmethod
    def transform_command(command):
        return {
            "input": {
                "method": command["method"],
                "args": [f"{arg[0]}={arg[1]}" for arg in command["args"]]
            },
            "result": {
                "status": None,
                "response": None,
                "reads": [],
                "writes": [{"key": arg[0], "value": arg[1]} for arg in command["args"]]
            }
        }
