#!/usr/bin/python

import os
import psycopg2
import sqlite3 as sl

from connection.config import config
from util.logger import get_logger

logger = get_logger(__name__)


def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        params = config()
        logger.debug('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)

        return conn
    except (Exception, psycopg2.DatabaseError) as error:
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


def query(command: str, values=None):
    try:
        with connect() as conn, conn.cursor() as cur:
            cur.execute(command, values)
            return cur.fetchone()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f"Database error: {error}")
