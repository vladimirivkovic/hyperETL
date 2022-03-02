#!/usr/bin/python

import os
import psycopg2
import sqlite3 as sl

from etl.config import config
from util.logger import get_logger

SQLITE_DB = "podw.db"
logger = get_logger(__name__)
DB = os.environ["DB"]

def connect():
    if DB == "postgres":
        return connect_to_postgres()
    else:
        return connect_to_sqlite()


def connect_to_postgres():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        params = config()
        logger.debug('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f"Connection error: {error}")


def connect_to_sqlite():
    """ Connect to built-in SQLite database """
    conn = None
    try:
        logger.debug('Connecting to the SQLite database...')
        conn = sl.connect(SQLITE_DB)
        return conn
    except Exception as error:
        logger.error(f"Connection error: {error}")


def execute(command: str, values=None, many=False):
    try:
        with connect() as conn, conn.cursor() as cur:
            if many:
                cur.executemany(command, values)
            else:
                cur.execute(command)

            conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f"Database error: {error}")
