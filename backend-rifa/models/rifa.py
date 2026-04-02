# models/rifa.py
from database.connection import db
from datetime import datetime

class Rifa:
    
    @staticmethod
    def listar_ativas():
        query = """
            SELECT id_rifa, nome, descricao, imagem, data_inicio, 
                   data_sorteio, valor_bilhete, premio, total_numeros, status
            FROM rifa 
            WHERE status = 'ativa' AND data_sorteio > NOW()
            ORDER BY data_sorteio ASC
        """
        cursor = db.execute_query(query)
        return cursor.fetchall()
    
    @staticmethod
    def buscar_por_id(id_rifa):
        query = """
            SELECT id_rifa, nome, descricao, imagem, data_inicio, 
                   data_sorteio, valor_bilhete, premio, total_numeros, status
            FROM rifa 
            WHERE id_rifa = %s
        """
        cursor = db.execute_query(query, (id_rifa,))
        return cursor.fetchone()
    
    @staticmethod
    def get_numeros_status(id_rifa):
        query = """
            SELECT numero, status, reserva_id, usuario_id
            FROM bilhete 
            WHERE rifa_id = %s
        """
        cursor = db.execute_query(query, (id_rifa,))
        bilhetes = cursor.fetchall()
        
        disponiveis = []
        reservados = []
        pagos = []
        
        for b in bilhetes:
            if b['status'] == 'disponivel':
                disponiveis.append(b['numero'])
            elif b['status'] == 'reservado':
                reservados.append(b['numero'])
            elif b['status'] == 'pago':
                pagos.append(b['numero'])
        
        return {
            'disponiveis': disponiveis,
            'reservados': reservados,
            'pagos': pagos
        }
    
    @staticmethod
    def get_valor_bilhete(id_rifa):
        query = "SELECT valor_bilhete FROM rifa WHERE id_rifa = %s"
        cursor = db.execute_query(query, (id_rifa,))
        result = cursor.fetchone()
        return result['valor_bilhete'] if result else None