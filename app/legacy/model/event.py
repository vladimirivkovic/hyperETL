class Event:
    def __init__(self, transaction):
        self.timestamp = transaction.header.timestamp
        self.activity = transaction.method
        self.args = ";".join(transaction.actions[0].input_["args"][1:])
        self.actor = transaction.actions[0].creator
        self.tx_id = transaction.header.tx_id
        self.response_status = str(transaction.actions[0].response["status"])
        payload = transaction.actions[0].response["payload"]
        self.response_payload = payload if payload != None else ""
        self.key = None

    def __str__(self):
        return f"{self.tx_id} - {self.activity} - {self.actor} - {self.args} - {self.timestamp}"
