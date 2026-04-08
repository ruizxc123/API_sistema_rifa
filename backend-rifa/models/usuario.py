# models/usuario.py
from database.connection import db
import hashlib

class Usuario:
    
    @staticmethod
    def criar(nome, email, cpf, telefone, senha):
        # Hash da senha com MD5 (simples para exemplo)
        senha_hash = hashlib.md5(senha.encode()).hexdigest()
        
        query = """
            INSERT INTO usuario (nome, email, cpf, telefone, senha)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (nome, email, cpf, telefone, senha_hash)
        
        cursor = db.execute_query(query, params)
        db.commit()
        
        return cursor.lastrowid
    

    
    @staticmethod
    def buscar_por_id(id_usuario):
        query = "SELECT id_usuario, nome, email, cpf, telefone, data_cadastro, status FROM usuario WHERE id_usuario = %s"
        cursor = db.execute_query(query, (id_usuario,))
        return cursor.fetchone()
    
    @staticmethod
    def autenticar(email, senha):
        senha_hash = hashlib.md5(senha.encode()).hexdigest()
        query = "SELECT * FROM usuario WHERE email = %s AND senha = %s AND status = 1"
        cursor = db.execute_query(query, (email, senha_hash))
        return cursor.fetchone()
    
    @staticmethod
    def atualizar(id_usuario, nome=None, telefone=None):
        if nome:
            query = "UPDATE usuario SET nome = %s WHERE id_usuario = %s"
            db.execute_query(query, (nome, id_usuario))
        
        if telefone:
            query = "UPDATE usuario SET telefone = %s WHERE id_usuario = %s"
            db.execute_query(query, (telefone, id_usuario))
        
        db.commit()
        return True
    
    @staticmethod
    def alterar_senha(id_usuario, senha_atual, nova_senha):
        # Verificar senha atual
        senha_hash_atual = hashlib.md5(senha_atual.encode()).hexdigest()
        query = "SELECT id_usuario FROM usuario WHERE id_usuario = %s AND senha = %s"
        cursor = db.execute_query(query, (id_usuario, senha_hash_atual))
        
        if not cursor.fetchone():
            return False
        
        # Atualizar senha
        nova_senha_hash = hashlib.md5(nova_senha.encode()).hexdigest()
        query = "UPDATE usuario SET senha = %s WHERE id_usuario = %s"
        db.execute_query(query, (nova_senha_hash, id_usuario))
        db.commit()
        
        return True
    
    @staticmethod
    def total_ativos():
        query = "SELECT COUNT(*) as total FROM usuario WHERE status = 1"
        cursor = db.execute_query(query)
        return cursor.fetchone()['total']

    @staticmethod
    def listar_todos():
        query = "SELECT id_usuario, nome, email, cpf, tipo, status, data_cadastro FROM usuario ORDER BY data_cadastro DESC"
        cursor = db.execute_query(query)
        return cursor.fetchall()

    @staticmethod
    def bloquear_desbloquear(id_usuario):
        query = "UPDATE usuario SET status = NOT status WHERE id_usuario = %s"
        db.execute_query(query, (id_usuario,))
        db.commit()