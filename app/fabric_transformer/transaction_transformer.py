from unicodedata import name
import jmespath

from util.logger import get_logger
from util.decoder import decode


class TransactionTransformer:
    def __init__(self) -> None:
        self.logger = get_logger(__name__)

    @staticmethod
    def transform(raw_transactions):
        payloads = jmespath.search('[*].payload', raw_transactions)

        if not payloads:
            return []
        else:
            return [TransactionTransformer.transform_payload(raw_payload) for raw_payload in payloads]

    @staticmethod
    def transform_payload(raw_payload):
        transaction = {}
        raw_actions = jmespath.search("data.actions", raw_payload)

        if not raw_actions:
            return None

        raw_header = jmespath.search("header", raw_payload)
        transaction["header"] = TransactionTransformer.transform_header(
            raw_header)
        transaction["data"] = [
            TransactionTransformer.transform_actions(a) for a in raw_actions]
        return transaction

    @staticmethod
    def transform_header(raw_header):
        channel_header = raw_header["channel_header"]
        return {
            "channel_id": channel_header["channel_id"],
            "smart_contract": jmespath.search("extension.chaincode_id", raw_header),
            "transaction_id": channel_header["tx_id"],
            "timestamp": channel_header["timestamp"],
            "creator": jmespath.search("signature_header.creator.mspid", raw_header)
        }

    @staticmethod
    def transform_actions(raw_action):
        # endosments_no = len(jmespath.search(
        #     "payload.action.endorsements", raw_action))
        # chaincode_id = jmespath.search(
        #     "payload.action.proposal_response_payload.extension.chaincode_id", raw_action)

        return {
            "input": TransactionTransformer.transform_input(raw_action),
            "result": TransactionTransformer.transform_response(raw_action)
        }

    @staticmethod
    def transform_input(raw_action):
        creator = jmespath.search("header.creator.mspid", raw_action)
        action_input = jmespath.search(
            "payload.chaincode_proposal_payload.input.chaincode_spec", raw_action)

        if "is_init" in action_input["input"]:
            action_input["is_init"] = action_input["input"]["is_init"]
        if "args" not in action_input:
            action_input["args"] = action_input["input"]["args"]
        action_input["args"] = [decode(a) for a in action_input["args"]]

        return {
            "method": action_input["args"][0],
            "args": action_input["args"][1:],
            "creator": creator
        }

    @staticmethod
    def transform_response(raw_action):
        response = jmespath.search(
            "payload.action.proposal_response_payload.extension.response", raw_action)
        response["payload"] = decode(response["payload"])

        rwset = jmespath.search(
            "payload.action.proposal_response_payload.extension.results.ns_rwset", raw_action)
        rwset = TransactionTransformer._decode_rwset_values(rwset)

        return {
            "status": response["status"],
            "response": response["payload"],
            **rwset
        }

    @staticmethod
    def _decode_rwset_values(rwset):
        ret = {"reads": [], "writes": []}
        for rws in rwset:
            namespace = rws["namespace"]
            for rs in rws["rwset"]["reads"]:
                value = decode(rs["value"]) if "value" in rs else None
                ret["reads"].append({
                    "key": rs["key"],
                    "value": value,
                    "version": rs["version"],
                    "namespace": namespace
                })
            for ws in rws["rwset"]["writes"]:
                value = decode(ws["value"]) if "value" in ws else None
                ret["writes"].append({
                    "key": ws["key"],
                    "value": value,
                    "is_delete": ws["is_delete"] if "is_delete" in ws else False,
                    "namespace": namespace
                })
        return ret
