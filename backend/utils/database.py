import logging

import mysql.connector
from mysql.connector import Error

from config import Config

logger = logging.getLogger(__name__)


def get_db():
    conn = None
    try:
        conn = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE,
            autocommit=False,
            connection_timeout=5,
        )
        cursor = conn.cursor()
        cursor.execute("SET time_zone = '+00:00'")
        cursor.close()
        return conn
    except Error:
        if conn is not None:
            conn.close()
        logger.exception("Não foi possível conectar ao banco de dados.")
        return None
