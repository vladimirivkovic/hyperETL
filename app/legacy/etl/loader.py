import os
from sqlite3 import OperationalError

from etl.connection import connect, execute, DB
from util.keys import replace_nonprintable
from util.logger import get_logger

# placeholder for values
PH = "?" if DB == "sqlite" else "%s"
logger = get_logger(__name__)

def load_blocks(blocks):
    logger.info("loading blocks ...")
    sql_insert = f"INSERT INTO blocks(block_num) VALUES({PH})"
    values = [b.to_sql_values() for b in blocks]
    execute(sql_insert, values, True)


def load_transactions(transactions):
    logger.info("loading transactions ...")
    sql_insert = f"INSERT INTO transactions(tx_id, block_num, tx_timestamp, channel_id, \
                                           chaincode_id, creator, endosments_no, \
                                           response_msg ,response_status, method) \
                        VALUES({PH}, {PH}, {PH}, {PH}, {PH}, {PH}, {PH}, {PH}, {PH}, {PH})"
    values = [tx.to_sql_values() for tx in transactions]
    execute(sql_insert, values, True)


def load_cc_args(transactions):
    logger.info("loading cc_args ...")
    sql_insert = f"INSERT INTO cc_args(arg_number, arg_value, tx_id) \
                        VALUES({PH}, {PH}, {PH})"
    values = []

    for tx in transactions:
        values.extend(tx.to_args_sql_values())

    execute(sql_insert, values, True)


def load_keys(keys):
    logger.info("loading keys ...")
    sql_insert = f"INSERT INTO keys(key_id, key_namespace) VALUES({PH}, {PH})"
    values = [k.to_sql_values() for k in keys]
    execute(sql_insert, values, True)


def load_key_history(keys):
    logger.info("loading key history ...")
    sql_insert = f"INSERT INTO key_history(key_id, tx_id, operation, payload, \
                                          is_delete, version_) \
                        VALUES({PH}, {PH}, {PH}, {PH}, {PH}, {PH})"
    values = []

    for k in keys:
        key_name = replace_nonprintable(k.key_name)
        values.extend([(key_name, *kh.to_sql_values()) for kh in k.history])

    execute(sql_insert, values, True)


def clear_all():
    logger.info("cleaining all data ...")
    sql_delete = "DELETE FROM {}"

    for table in ["key_history", "keys", "cc_args", "transactions", "blocks"]:
        execute(sql_delete.format(table))


def init_db():
    logger.info("recreating tables ...")

    with connect() as conn:
        execute_sql_script(conn, "db/schema.sql")


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
