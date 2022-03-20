import os

from connection.postgres import execute, connect, query
from util.keys import replace_nonprintable
from util.logger import get_logger

PH = "%s"
logger = get_logger(__name__)


def generate_sql_insert(table, columns):
    columns_list = ",".join(columns)
    placheholders = (("," + PH) * len(columns))[1:]
    return f"INSERT INTO {table}({columns_list}) VALUES({placheholders})"


def load_blocks(blocks):
    logger.info("loading blocks ...")
    columns = ["block_num", "block_hash", "previous_block_hash", "block_timestamp",
               "signature", "blockchain_type", "blockchain_version", "blockchain_source"]
    values = [block_to_sql_values(b) for b in blocks]
    execute(generate_sql_insert("blocks", columns), values, True)


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


def load_transactions(blocks):
    logger.info("loading transactions ...")
    columns = ["transaction_hash", "transaction_timestamp", "smart_contract",
               "creator", "method", "response", "status", "block_id"]
    sql_insert = generate_sql_insert("transactions", columns)

    for block in blocks:
        block_id = query(
            f"SELECT block_id FROM blocks WHERE block_hash = {PH}", (block["header"]["block_hash"], ))
        logger.info(block_id)
        values = [tx_to_sql_values(tx) + (block_id, )
                  for tx in block["transactions"] if tx is not None]
        execute(sql_insert, values, True)


# def load_sc_args(transactions):
#     logger.info("loading cc_args ...")
#     sql_insert = f"INSERT INTO cc_args(arg_number, arg_value, tx_id) \
#                         VALUES({PH}, {PH}, {PH})"
#     values = []

#     for tx in transactions:
#         values.extend(tx.to_args_sql_values())

#     execute(sql_insert, values, True)


# def load_operations(keys):
#     logger.info("loading key history ...")
#     sql_insert = f"INSERT INTO key_history(key_id, tx_id, operation, payload, \
#                                           is_delete, version_) \
#                         VALUES({PH}, {PH}, {PH}, {PH}, {PH}, {PH})"
#     values = []

#     for k in keys:
#         key_name = replace_nonprintable(k.key_name)
#         values.extend([(key_name, *kh.to_sql_values()) for kh in k.history])

#     execute(sql_insert, values, True)


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
