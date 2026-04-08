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
    
    @staticmethod
    def listar_todas():
        query = "SELECT * FROM rifa ORDER BY data_sorteio DESC"
        cursor = db.execute_query(query)
        return cursor.fetchall()

    @staticmethod
    def criar(dados):
        query = """INSERT INTO rifa (nome, descricao, imagem, data_inicio, data_sorteio,
                                    valor_bilhete, premio, total_numeros, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'ativa')"""
        params = (dados['nome'], dados['descricao'], dados['imagem'], dados['data_inicio'],
                dados['data_sorteio'], dados['valor_bilhete'], dados['premio'], dados['total_numeros'])
        cursor = db.execute_query(query, params)
        db.commit()
        return cursor.lastrowid

    @staticmethod
    def atualizar(id_rifa, dados):
        query = """UPDATE rifa SET nome=%s, descricao=%s, imagem=%s, data_inicio=%s,
                data_sorteio=%s, valor_bilhete=%s, premio=%s, total_numeros=%s
                WHERE id_rifa=%s"""
        params = (dados['nome'], dados['descricao'], dados['imagem'], dados['data_inicio'],
                dados['data_sorteio'], dados['valor_bilhete'], dados['premio'], dados['total_numeros'], id_rifa)
        db.execute_query(query, params)
        db.commit()

    @staticmethod
    def total_ativas():
        query = "SELECT COUNT(*) as total FROM rifa WHERE status='ativa'"
        cursor = db.execute_query(query)
        return cursor.fetchone()['total']

    @staticmethod
    def encerrar(id_rifa):
        query = "UPDATE rifa SET status='encerrada' WHERE id_rifa=%s"
        db.execute_query(query, (id_rifa,))
        db.commit()

    @staticmethod
    def cancelar(id_rifa):
        query = "UPDATE rifa SET status='cancelada' WHERE id_rifa=%s"
        db.execute_query(query, (id_rifa,))
        db.commit()