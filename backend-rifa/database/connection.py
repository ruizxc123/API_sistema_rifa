# database/connection.py
import mysql.connector
from mysql.connector import Error
from config import Config

class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        try:
            self.connection = mysql.connector.connect(
                host=Config.MYSQL_HOST,
                user=Config.MYSQL_USER,
                password=Config.MYSQL_PASSWORD,
                database=Config.MYSQL_DATABASE,
                autocommit=True
            )
            self.cursor = self.connection.cursor(dictionary=True)
            print("✅ Conectado ao MySQL com sucesso!")
        except Error as e:
            print(f"❌ Erro ao conectar ao MySQL: {e}")
            self.connection = None
            self.cursor = None
    
    def get_cursor(self):
        if self.connection is None or not self.connection.is_connected():
            self._initialize()
        return self.connection.cursor(dictionary=True)
    
    def commit(self):
        if self.connection:
            self.connection.commit()
    
    def close(self):
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
    
    def execute_query(self, query, params=None):
        cursor = self.get_cursor()
        try:
            cursor.execute(query, params or ())
            return cursor
        except Error as e:
            print(f"❌ Erro na query: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            raise e

# Instância global
db = Database()