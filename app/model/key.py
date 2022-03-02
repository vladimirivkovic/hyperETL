from dataclasses import dataclass
from util.keys import replace_nonprintable
from model.transaction import Transaction

READ = "read"
RANGE_QUERY = "range_query"
WRITE = "write"


class Key:
    separator = '\u0000'
    wildcard = '#'

    def __init__(self, key_name, history=None):
        self.key_name = key_name
        self.history = [] if history == None else history[0].namespace
        self.composite = Key.separator in self.key_name
        self.components = self._decompose()

    def _decompose(self):
        components = self.key_name.split(Key.separator)
        if components[0] == '':
            del components[0]
        if components[-1] == '':
            del components[-1]
        return components

    def get_namespace(self):
        return None if self.history == None else self.history[0].namespace

    def first_transaction_id(self):
        if self.history:
            return self.history[0].transaction.header.tx_id
        return None

    def to_sql_values(self):
        return (replace_nonprintable(self.key_name), self.get_namespace())


@dataclass
class KeyChange:
    transaction: Transaction
    rwset: dict
    namespace: str
    type_: str

    def to_sql_values(self):
        op = ""
        if self.type_ == READ:
            op = 'R'
        elif self.type_ == RANGE_QUERY:
            op = 'Q'
        elif self.type_ == WRITE:
            op = 'W'

        value = self.rwset["value"] if "value" in self.rwset else None
        is_delete = self.rwset["is_delete"] if "is_delete" in self.rwset else None
        version = str(self.rwset["version"]) if "version" in self.rwset and self.rwset["version"] else None

        return (self.transaction.header.tx_id, op,
                replace_nonprintable(value), is_delete, version)
