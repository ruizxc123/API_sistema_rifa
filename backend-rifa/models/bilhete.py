# models/bilhete.py
from database.connection import db
from datetime import datetime

class Bilhete:
    
    @staticmethod
    def verificar_disponibilidade(rifa_id, numeros):
        placeholders = ','.join(['%s'] * len(numeros))
        query = f"""
            SELECT numero, status 
            FROM bilhete 
            WHERE rifa_id = %s AND numero IN ({placeholders})
        """
        params = [rifa_id] + numeros
        cursor = db.execute_query(query, tuple(params))
        
        bilhetes = cursor.fetchall()
        indisponiveis = [b['numero'] for b in bilhetes if b['status'] != 'disponivel']
        
        return len(indisponiveis) == 0, indisponiveis
    
    @staticmethod
    def reservar_numeros(rifa_id, numeros, reserva_id):
        placeholders = ','.join(['%s'] * len(numeros))
        query = f"""
            UPDATE bilhete 
            SET status = 'reservado', reserva_id = %s
            WHERE rifa_id = %s AND numero IN ({placeholders}) AND status = 'disponivel'
        """
        params = [reserva_id, rifa_id] + numeros
        db.execute_query(query, tuple(params))
        db.commit()
        
        return True
    
    @staticmethod
    def confirmar_pagamento(reserva_id, usuario_id):
        query = """
            UPDATE bilhete 
            SET status = 'pago', usuario_id = %s, data_compra = NOW()
            WHERE reserva_id = %s AND status = 'reservado'
        """
        db.execute_query(query, (usuario_id, reserva_id))
        db.commit()
        
        return True
    
    @staticmethod
    def liberar_reserva(reserva_id):
        query = """
            UPDATE bilhete 
            SET status = 'disponivel', reserva_id = NULL
            WHERE reserva_id = %s AND status = 'reservado'
        """
        db.execute_query(query, (reserva_id,))
        db.commit()
        
        return True
    
    @staticmethod
    def get_meus_bilhetes(usuario_id):
        query = """
            SELECT 
                b.id_bilhete,
                b.numero,
                b.data_compra,
                r.nome as rifa_nome,
                r.premio,
                r.data_sorteio,
                r.valor_bilhete,
                s.numero_sorteado,
                CASE 
                    WHEN s.numero_sorteado = b.numero THEN 1 
                    ELSE 0 
                END as premiado
            FROM bilhete b
            INNER JOIN rifa r ON b.rifa_id = r.id_rifa
            LEFT JOIN sorteio s ON r.id_rifa = s.rifa_id
            WHERE b.usuario_id = %s AND b.status = 'pago'
            ORDER BY b.data_compra DESC
        """
        cursor = db.execute_query(query, (usuario_id,))
        return cursor.fetchall()
        
    @staticmethod
    def criar_para_rifa(rifa_id, numero):
        query = "INSERT INTO bilhete (rifa_id, numero, status) VALUES (%s, %s, 'disponivel')"
        db.execute_query(query, (rifa_id, numero))
        db.commit()

    @staticmethod
    def total_pagos():
        query = "SELECT COUNT(*) as total FROM bilhete WHERE status='pago'"
        cursor = db.execute_query(query)
        return cursor.fetchone()['total']

    @staticmethod
    def numeros_pagos_por_rifa(rifa_id):
        query = "SELECT numero FROM bilhete WHERE rifa_id=%s AND status='pago'"
        cursor = db.execute_query(query, (rifa_id,))
        return [row['numero'] for row in cursor.fetchall()]

    @staticmethod
    def buscar_por_numero(rifa_id, numero):
        query = "SELECT * FROM bilhete WHERE rifa_id=%s AND numero=%s"
        cursor = db.execute_query(query, (rifa_id, numero))
        return cursor.fetchone()

    @staticmethod
    def atualizar_status(rifa_id, numero, novo_status):
        query = "UPDATE bilhete SET status=%s WHERE rifa_id=%s AND numero=%s"
        db.execute_query(query, (novo_status, rifa_id, numero))
        db.commit()