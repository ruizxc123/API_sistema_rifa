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
    
    @staticmethod
    def total_aprovado():
        query = "SELECT SUM(valor) as total FROM pagamento WHERE status='aprovado'"
        cursor = db.execute_query(query)
        return cursor.fetchone()['total'] or 0

    @staticmethod
    def listar_com_filtros(filtros):
        query = """SELECT p.*, u.nome as usuario_nome, r.nome as rifa_nome
                FROM pagamento p
                JOIN usuario u ON p.usuario_id = u.id_usuario
                JOIN reserva res ON p.reserva_id = res.id_reserva
                JOIN bilhete b ON res.id_reserva = b.reserva_id
                JOIN rifa r ON b.rifa_id = r.id_rifa
                WHERE 1=1"""
        params = []
        if filtros.get('rifa_id'):
            query += " AND r.id_rifa = %s"
            params.append(filtros['rifa_id'])
        if filtros.get('status'):
            query += " AND p.status = %s"
            params.append(filtros['status'])
        if filtros.get('data_inicio'):
            query += " AND p.data_pagamento >= %s"
            params.append(filtros['data_inicio'])
        if filtros.get('data_fim'):
            query += " AND p.data_pagamento <= %s"
            params.append(filtros['data_fim'])
        query += " GROUP BY p.id_pagamento ORDER BY p.data_pagamento DESC"
        cursor = db.execute_query(query, tuple(params))
        return cursor.fetchall()