# models/reserva.py
from database.connection import db
from datetime import datetime, timedelta
from config import Config

class Reserva:
    
    @staticmethod
    def criar(usuario_id, rifa_id, numeros):
        # Calcular valor total
        valor_bilhete = None
        query_valor = "SELECT valor_bilhete FROM rifa WHERE id_rifa = %s"
        cursor = db.execute_query(query_valor, (rifa_id,))
        result = cursor.fetchone()
        valor_bilhete = result['valor_bilhete']
        valor_total = valor_bilhete * len(numeros)
        
        # Data de expiração
        data_expiracao = datetime.now() + timedelta(minutes=Config.RESERVA_TIMEOUT_MINUTES)
        
        # Criar reserva
        query_reserva = """
            INSERT INTO reserva (data_expiracao, usuario_id)
            VALUES (%s, %s)
        """
        cursor = db.execute_query(query_reserva, (data_expiracao, usuario_id))
        reserva_id = cursor.lastrowid
        
        # Reservar os números
        from models.bilhete import Bilhete
        Bilhete.reservar_numeros(rifa_id, numeros, reserva_id)
        
        db.commit()
        
        return {
            'reserva_id': reserva_id,
            'expira_em': data_expiracao.strftime('%Y-%m-%d %H:%M:%S'),
            'numeros': numeros,
            'valor_total': float(valor_total)
        }
    
    @staticmethod
    def get_ativas_por_usuario(usuario_id):
        query = """
            SELECT 
                r.id_reserva,
                r.data_expiracao,
                r.status,
                rif.nome as rifa_nome,
                rif.valor_bilhete,
                GROUP_CONCAT(b.numero ORDER BY b.numero) as numeros
            FROM reserva r
            INNER JOIN bilhete b ON r.id_reserva = b.reserva_id
            INNER JOIN rifa rif ON b.rifa_id = rif.id_rifa
            WHERE r.usuario_id = %s AND r.status = 'ativa' AND r.data_expiracao > NOW()
            GROUP BY r.id_reserva
        """
        cursor = db.execute_query(query, (usuario_id,))
        reservas = cursor.fetchall()
        
        for reserva in reservas:
            reserva['numeros'] = [int(n) for n in reserva['numeros'].split(',')]
            reserva['valor_total'] = float(reserva['valor_bilhete'] * len(reserva['numeros']))
        
        return reservas
    
    @staticmethod
    def get_by_id(reserva_id):
        query = """
            SELECT r.*, rif.valor_bilhete
            FROM reserva r
            INNER JOIN bilhete b ON r.id_reserva = b.reserva_id
            INNER JOIN rifa rif ON b.rifa_id = rif.id_rifa
            WHERE r.id_reserva = %s
            LIMIT 1
        """
        cursor = db.execute_query(query, (reserva_id,))
        return cursor.fetchone()
    
    @staticmethod
    def cancelar(reserva_id, usuario_id):
        # Verificar se a reserva pertence ao usuário
        query_check = """
            SELECT id_reserva FROM reserva 
            WHERE id_reserva = %s AND usuario_id = %s AND status = 'ativa'
        """
        cursor = db.execute_query(query_check, (reserva_id, usuario_id))
        
        if not cursor.fetchone():
            return False
        
        # Atualizar status da reserva
        query_update = "UPDATE reserva SET status = 'expirada' WHERE id_reserva = %s"
        db.execute_query(query_update, (reserva_id,))
        
        # Liberar os bilhetes
        from models.bilhete import Bilhete
        Bilhete.liberar_reserva(reserva_id)
        
        db.commit()
        return True
    
    @staticmethod
    def converter_para_pago(reserva_id, usuario_id):
        # Atualizar status da reserva
        query = "UPDATE reserva SET status = 'convertida' WHERE id_reserva = %s"
        db.execute_query(query, (reserva_id,))
        
        # Confirmar pagamento dos bilhetes
        from models.bilhete import Bilhete
        Bilhete.confirmar_pagamento(reserva_id, usuario_id)
        
        db.commit()
        return True