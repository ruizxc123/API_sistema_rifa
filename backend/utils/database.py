import logging

import mysql.connector
from mysql.connector import Error

from config import Config

logger = logging.getLogger(__name__)


def get_db():
    try:
        return mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE,
            autocommit=False,
            connection_timeout=5,
        )
    except Error:
        logger.exception("Não foi possível conectar ao banco de dados.")
        return None
