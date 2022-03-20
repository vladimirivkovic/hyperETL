from dataclasses import dataclass


@dataclass
class Block:
    header: dict
    raw_transactions: list

    @property
    def number(self):
        return self.header['number']

    def to_sql_values(self):
        return (self.number,)
