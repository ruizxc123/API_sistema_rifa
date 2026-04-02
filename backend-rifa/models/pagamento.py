# models/pagamento.py
from database.connection import db

class Pagamento:
    
    @staticmethod
    def criar(reserva_id, usuario_id, valor, metodo):
        query = """
            INSERT INTO pagamento (valor, metodo, status, reserva_id, usuario_id)
            VALUES (%s, %s, 'aprovado', %s, %s)
        """
        db.execute_query(query, (valor, metodo, reserva_id, usuario_id))
        db.commit()
        
        return db.cursor.lastrowid