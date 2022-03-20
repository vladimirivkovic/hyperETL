from dataclasses import dataclass
from model.block import Block


@dataclass
class Transaction:
    header: dict
    actions: list
    block: Block

    @property
    def method(self):
        return self.actions[0].method

    def get_rw_sets(self):
        read_sets = []
        rq_sets = []
        write_sets = []

        for action in self.actions:
            for rwset in action.rwset:
                # if rwset["namespace"] == cc:
                for rws in rwset["rwset"]["reads"]:
                    read_sets.append((rws, rwset["namespace"]))

                for rqi in rwset["rwset"]["range_queries_info"]:
                    for rws in rqi["raw_reads"]["kv_reads"]:
                        rq_sets.append((rws, rwset["namespace"]))

                for rws in rwset["rwset"]["writes"]:
                    write_sets.append((rws, rwset["namespace"]))

        return read_sets, rq_sets, write_sets

    def get_keys(self):
        keys = []

        read_sets, rq_sets, write_sets = self.get_rw_sets()
        for rws in read_sets + rq_sets + write_sets:
            keys.append(rws)

        return keys

    def get_read_keys(self, namespace):
        read_sets, rq_sets, write_sets = self.get_rw_sets()
        return set([rws[0]["key"]
                    for rws in read_sets + rq_sets if rws[1] == namespace])

    def get_write_keys(self, namespace):
        read_sets, rq_sets, write_sets = self.get_rw_sets()
        return set([rws[0]["key"]
                    for rws in write_sets if rws[1] == namespace])

    def is_init(self):
        return self.actions[0].input.get("is_init")

    def get_chaincode_name(self):
        chaincode_name = self.header.get_chaincode_name()

        if chaincode_name:
            return chaincode_name

        return self.actions[0].chaincode_id["name"]

    def to_sql_values(self):
        return (self.header.tx_id, self.block.number, self.header.timestamp,
                self.header.channel_id, self.get_chaincode_name(),
                self.actions[0].creator, self.actions[0].endosments_no,
                self.actions[0].response["message"], self.actions[0].response["status"], self.method)

    def to_args_sql_values(self):
        values = []

        for i, arg in enumerate(self.actions[0].input_["args"]):
            if i == 0:
                continue
            values.append(
                (i, self.actions[0].input_["args"][i], self.header.tx_id))

        return values


@dataclass
class Action:
    creator: str
    endosments_no: int
    chaincode_id: dict
    response: dict
    rwset: list
    input_: dict

    @property
    def namespace(self):
        return self._get_namespaces()

    @property
    def method(self):
        return self._get_method()

    def _get_namespaces(self):
        ret_val = set()
        for rwset in self.rwset:
            ret_val.add(rwset["namespace"])
        return ret_val

    def _get_method(self):
        return "" if len(self.input_["args"]) == 0 else self.input_["args"][0]


@dataclass
class TransactionHeader:
    channel_id: str
    chaincode_id: dict
    timestamp: str
    tx_id: str

    def get_chaincode_name(self):
        if isinstance(self.chaincode_id, dict):
            return self.chaincode_id["name"]
        return self.chaincode_id
