from functools import wraps
from flask import request, jsonify
import jwt
from config import Config

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'erro': 'Token não fornecido'}), 401
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            current_user = data['usuario_id']
        except:
            return jsonify({'erro': 'Token inválido'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(current_user, *args, **kwargs):
        from utils.database import get_db
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT tipo FROM usuario WHERE id_usuario = %s', (current_user,))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()
        if not usuario or usuario['tipo'] != 'admin':
            return jsonify({'erro': 'Acesso negado'}), 403
        return f(current_user, *args, **kwargs)
    return decorated