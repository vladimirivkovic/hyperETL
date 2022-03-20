import base64
import jmespath

from model.transaction import Transaction, Action, TransactionHeader


class TransactionExtractor:
    def __init__(self, block):
        self.transactions = self._extract_from_block(block)

    def _extract_from_block(self, block):
        payloads = jmespath.search('[*].payload', block.raw_transactions)
        return [Transaction(*payload, block) for p in payloads if (payload := TransactionExtractor._clean_payload(p))]

        # for 3.7
        # ret_val = []

        # for p in payloads:
        #     payload = TransactionExtractor._clean_payload(p)
        #     if payload:
        #         ret_val.append(Transaction(*payload, block))

        # return ret_val

    @staticmethod
    def _clean_payload(payload_raw):
        actions_raw = jmespath.search("data.actions", payload_raw)

        if not actions_raw:
            return None

        header_raw = jmespath.search("header", payload_raw)
        actions = [TransactionExtractor._clean_action(a) for a in actions_raw]
        header = TransactionExtractor._clean_header(header_raw)
        return header, actions

    @staticmethod
    def _clean_action(action_raw):
        creator = jmespath.search("header.creator.mspid", action_raw)
        endosments_no = len(jmespath.search(
            "payload.action.endorsements", action_raw))
        chaincode_id = jmespath.search(
            "payload.action.proposal_response_payload.extension.chaincode_id", action_raw)

        response = jmespath.search(
            "payload.action.proposal_response_payload.extension.response", action_raw)
        response["payload"] = TransactionExtractor._decode(response["payload"])
        rwset = jmespath.search(
            "payload.action.proposal_response_payload.extension.results.ns_rwset", action_raw)
        rwset = TransactionExtractor._decode_rwset_values(rwset)

        action_input = jmespath.search(
            "payload.chaincode_proposal_payload.input.chaincode_spec", action_raw)

        if "is_init" in action_input["input"]:
            action_input["is_init"] = action_input["input"]["is_init"]
        if "args" not in action_input:
            action_input["args"] = action_input["input"]["args"]
            del action_input["input"]

        action_input["args"] = [TransactionExtractor._decode(a) for a in action_input["args"]]

        return Action(creator, endosments_no, chaincode_id, response, rwset, action_input)

    @staticmethod
    def _decode_rwset_values(rwset):
        for rws in rwset:
            for rs in rws["rwset"]["reads"]:
                rs["value"] = TransactionExtractor._decode(
                    rs["value"]) if "value" in rs else None
            for ws in rws["rwset"]["writes"]:
                ws["value"] = TransactionExtractor._decode(
                    ws["value"]) if "value" in ws else None
        return rwset

    @staticmethod
    def _clean_header(header_raw):
        header = header_raw["channel_header"]
        chaincode_id = jmespath.search("extension.chaincode_id", header_raw)
        return TransactionHeader(header["channel_id"], chaincode_id, header["timestamp"], header["tx_id"])

    @staticmethod
    def _decode(content):
        if content == None:
            return None
        try:
            return base64.b64decode(content).decode()
        except:
            return content
