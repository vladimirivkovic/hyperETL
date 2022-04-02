from connection.postgres import execute, connect, query
from util.keys import replace_nonprintable
from util.logger import get_logger

PH = "%s"
logger = get_logger(__name__)


def generate_sql_insert(table, columns):
    columns_list = ",".join(columns)
    placheholders = (("," + PH) * len(columns))[1:]
    return f"INSERT INTO {table}({columns_list}) VALUES({placheholders})"


def get_all_transactions(blocks):
    transactions = []

    for block in blocks:
        transactions.extend([tx for tx in block["transactions"] if tx])

    return transactions


def block_to_sql_values(block):
    return (block["header"]["block_number"], block["header"]["block_hash"],
            block["header"]["previous_block_hash"], block["header"]["timestamp"],
            block["header"]["signer"], block["metadata"]["blockchain"],
            block["metadata"]["version"], block["metadata"]["source"])


def tx_to_sql_values(tx):
    return (tx["header"]["transaction_id"], tx["header"]["timestamp"],
            tx["header"]["smart_contract"], tx["header"]["creator"],
            tx["data"][0]["input"]["method"] if len(tx["data"]) > 0 else None,
            tx["data"][0]["result"]["response"] if len(
                tx["data"]) > 0 else None,
            tx["data"][0]["result"]["status"] if len(tx["data"]) > 0 else None)


def read_to_sql_values(r):
    return (replace_nonprintable(r["key"])), "R", None, False, str(r["version"], )


def write_to_sql_values(w):
    return (replace_nonprintable(w["key"]), "W", replace_nonprintable(w["value"]),
            w["is_delete"] if "is_delete" in w else None, None, )


def get_id_by_hash(table, hash):
    ret_id = query(
        f"SELECT {table}_id FROM {table}s WHERE {table}_hash = {PH}", (hash, ))

    if not ret_id:
        logger.warn(
            f"{table} with provided hash not found: setting {table}_id to 1")
        ret_id = 1

    return ret_id


def load_blocks(blocks):
    logger.info("loading blocks ...")
    columns = ["block_num", "block_hash", "previous_block_hash", "block_timestamp",
               "signature", "blockchain_type", "blockchain_version", "blockchain_source"]
    values = [block_to_sql_values(b) for b in blocks]
    execute(generate_sql_insert("blocks", columns), values, True)


def load_transactions(blocks):
    logger.info("loading transactions ...")
    columns = ["transaction_hash", "transaction_timestamp", "smart_contract",
               "creator", "method", "response", "status", "block_id"]
    sql_insert = generate_sql_insert("transactions", columns)

    for block in blocks:
        block_id = get_id_by_hash("block", block["header"]["block_hash"])

        values = [tx_to_sql_values(tx) + (block_id, )
                  for tx in block["transactions"] if tx is not None]
        execute(sql_insert, values, True)


def load_sc_args(blocks):
    logger.info("loading sc_args ...")
    columns = ["arg_number", "arg_value", "transaction_id"]
    sql_insert = generate_sql_insert("sc_args", columns)

    values = []

    for tx in get_all_transactions(blocks):
        tx_id = get_id_by_hash("transaction", tx["header"]["transaction_id"])

        arg_number = 1
        for data in tx["data"]:
            for arg in data["input"]["args"]:
                values.append((arg_number, arg, tx_id, ))
                arg_number += 1

    execute(sql_insert, values, True)


def load_operations(blocks):
    logger.info("loading key history ...")
    columns = ["key_id", "operation_type", "payload",
               "is_delete", "version_", "transaction_id"]
    sql_insert = generate_sql_insert("operations", columns)

    values = []

    for tx in get_all_transactions(blocks):
        tx_id = get_id_by_hash("transaction", tx["header"]["transaction_id"])

        for data in tx["data"]:
            for r in data["result"]["reads"]:
                values.append(read_to_sql_values(r) + (tx_id, ))
            for w in data["result"]["writes"]:
                values.append(write_to_sql_values(w) + (tx_id, ))

    execute(sql_insert, values, True)


def clear_all():
    logger.info("cleaining all data ...")
    sql_delete = "DELETE FROM {}"

    for table in ["operations", "sc_args", "transactions", "blocks"]:
        execute(sql_delete.format(table))


def init_db():
    logger.info("recreating tables ...")

    with connect() as conn:
        execute_sql_script(conn, "schema/db_schema.sql")


def execute_sql_script(conn, filename):
    fd = open(filename, 'r')
    sqlFile = fd.read()
    fd.close()

    sqlCommands = sqlFile.split(';')

    for command in sqlCommands:
        if command.strip() == "":
            continue
        with conn.cursor() as curr:
            curr.execute(command)
