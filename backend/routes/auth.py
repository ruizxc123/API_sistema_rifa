from flask import Blueprint, request, jsonify
from utils.database import get_db
import hashlib
import jwt
import datetime
from config import Config
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# Decorator para verificar token
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
        except Exception as e:
            print(f"❌ Erro no token: {e}")
            return jsonify({'erro': 'Token inválido'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@auth_bp.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        senha = data.get('senha')
        
        if not email or not senha:
            return jsonify({'erro': 'Email e senha obrigatórios'}), 400
        
        senha_hash = hashlib.md5(senha.encode()).hexdigest()
        conn = get_db()
        
        if not conn:
            return jsonify({'erro': 'Erro no banco'}), 500
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id_usuario, nome, email, tipo FROM usuario WHERE email = %s AND senha = %s AND status = 1', (email, senha_hash))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not usuario:
            return jsonify({'erro': 'Email ou senha inválidos'}), 401
        
        token = jwt.encode({
            'usuario_id': usuario['id_usuario'],
            'usuario_nome': usuario['nome'],
            'tipo': usuario['tipo'],
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
        }, Config.SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'sucesso': True,
            'token': token,
            'usuario': {
                'id_usuario': usuario['id_usuario'],
                'nome': usuario['nome'],
                'email': usuario['email'],
                'tipo': usuario['tipo']
            }
        })
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return jsonify({'erro': str(e)}), 500

@auth_bp.route('/api/usuarios/registrar', methods=['POST'])
def registrar():
    try:
        data = request.get_json()
        nome = data.get('nome')
        email = data.get('email')
        cpf = data.get('cpf')
        telefone = data.get('telefone')
        senha = data.get('senha')
        
        if not all([nome, email, cpf, telefone, senha]):
            return jsonify({'erro': 'Todos campos obrigatórios'}), 400
        
        senha_hash = hashlib.md5(senha.encode()).hexdigest()
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('INSERT INTO usuario (nome, email, cpf, telefone, senha, tipo) VALUES (%s, %s, %s, %s, %s, "user")', (nome, email, cpf, telefone, senha_hash))
        conn.commit()
        usuario_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return jsonify({'sucesso': True, 'mensagem': 'Usuário cadastrado', 'usuario_id': usuario_id}), 201
    except Exception as e:
        print(f"❌ Erro no registro: {e}")
        return jsonify({'erro': str(e)}), 500

@auth_bp.route('/api/session', methods=['GET'])
def get_session():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'usuario_id': None})
    try:
        if token.startswith('Bearer '):
            token = token[7:]
        data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        
        # Buscar dados completos do usuário no banco
        from utils.database import get_db
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT id_usuario, nome, email, cpf, telefone, tipo FROM usuario WHERE id_usuario = %s', (data['usuario_id'],))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not usuario:
            return jsonify({'usuario_id': None})
        
        return jsonify({
            'usuario_id': usuario['id_usuario'],
            'usuario': {
                'nome': usuario['nome'],
                'email': usuario['email'],
                'cpf': usuario['cpf'],
                'telefone': usuario['telefone'],
                'tipo': usuario['tipo']
            }
        })
    except Exception as e:
        print(f"Erro na sessão: {e}")
        return jsonify({'usuario_id': None})

@auth_bp.route('/api/reservas/criar', methods=['POST'])
@token_required
def criar_reserva(current_user):
    try:
        data = request.get_json()
        rifa_id = data.get('rifa_id')
        numeros = data.get('numeros')
        
        print(f"🔍 Criando reserva - Usuário: {current_user}, Rifa: {rifa_id}, Números: {numeros}")
        
        if not rifa_id or not numeros:
            return jsonify({'erro': 'Rifa e números são obrigatórios'}), 400
        
        conn = get_db()
        if not conn:
            return jsonify({'erro': 'Erro de conexão com o banco'}), 500
        
        cursor = conn.cursor(dictionary=True)
        
        # Verificar disponibilidade
        placeholders = ','.join(['%s'] * len(numeros))
        query = f'SELECT numero FROM bilhete WHERE rifa_id = %s AND numero IN ({placeholders}) AND status != "disponivel"'
        params = [rifa_id] + numeros
        cursor.execute(query, params)
        indisponiveis = cursor.fetchall()
        
        if indisponiveis:
            cursor.close()
            conn.close()
            return jsonify({
                'erro': 'Alguns números não estão disponíveis',
                'indisponiveis': [i['numero'] for i in indisponiveis]
            }), 400
        
        # Buscar valor do bilhete
        cursor.execute('SELECT valor_bilhete FROM rifa WHERE id_rifa = %s', (rifa_id,))
        rifa = cursor.fetchone()
        valor_bilhete = rifa['valor_bilhete']
        valor_total = valor_bilhete * len(numeros)
        
        # Criar reserva
        data_expiracao = datetime.datetime.now() + datetime.timedelta(minutes=5)
        cursor.execute('''
            INSERT INTO reserva (data_expiracao, usuario_id, status)
            VALUES (%s, %s, 'ativa')
        ''', (data_expiracao, current_user))
        reserva_id = cursor.lastrowid
        
        # Reservar números
        for numero in numeros:
            cursor.execute('''
                UPDATE bilhete 
                SET status = 'reservado', reserva_id = %s
                WHERE rifa_id = %s AND numero = %s AND status = 'disponivel'
            ''', (reserva_id, rifa_id, numero))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ Reserva {reserva_id} criada com sucesso")
        
        return jsonify({
            'reserva_id': reserva_id,
            'expira_em': data_expiracao.strftime('%Y-%m-%d %H:%M:%S'),
            'numeros': numeros,
            'valor_total': float(valor_total)
        }), 201
        
    except Exception as e:
        print(f"❌ Erro ao criar reserva: {e}")
        return jsonify({'erro': str(e)}), 500

@auth_bp.route('/api/reservas/ativas', methods=['GET'])
@token_required
def get_reservas_ativas(current_user):
    from utils.database import get_db
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # Primeiro, buscar as reservas ativas
    cursor.execute('''
        SELECT id_reserva, data_expiracao
        FROM reserva
        WHERE usuario_id = %s AND status = 'ativa' AND data_expiracao > NOW()
    ''', (current_user,))
    
    reservas = cursor.fetchall()
    
    resultado = []
    for r in reservas:
        # Buscar os bilhetes de cada reserva
        cursor.execute('''
            SELECT b.numero, rif.nome as rifa_nome, rif.valor_bilhete
            FROM bilhete b
            INNER JOIN rifa rif ON b.rifa_id = rif.id_rifa
            WHERE b.reserva_id = %s
        ''', (r['id_reserva'],))
        
        bilhetes = cursor.fetchall()
        
        if bilhetes:
            numeros = [b['numero'] for b in bilhetes]
            resultado.append({
                'id_reserva': r['id_reserva'],
                'data_expiracao': r['data_expiracao'].strftime('%Y-%m-%d %H:%M:%S'),
                'rifa_nome': bilhetes[0]['rifa_nome'],
                'numeros': numeros,
                'valor_total': float(bilhetes[0]['valor_bilhete'] * len(numeros))
            })
    
    cursor.close()
    conn.close()
    
    return jsonify(resultado)

@auth_bp.route('/api/reservas/<int:reserva_id>/cancelar', methods=['DELETE'])
@token_required
def cancelar_reserva(current_user, reserva_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE reserva SET status = "expirada" WHERE id_reserva = %s AND usuario_id = %s', (reserva_id, current_user))
    cursor.execute('UPDATE bilhete SET status = "disponivel", reserva_id = NULL WHERE reserva_id = %s', (reserva_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'sucesso': True})

@auth_bp.route('/api/meus-bilhetes', methods=['GET'])
@token_required
def get_meus_bilhetes(current_user):
    from utils.database import get_db
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # Buscar bilhetes com informações de sorteio
    cursor.execute('''
        SELECT 
            b.id_bilhete,
            b.numero,
            b.data_compra,
            r.id_rifa,
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
    ''', (current_user,))
    
    bilhetes = cursor.fetchall()
    cursor.close()
    conn.close()
    
    resultado = []
    for b in bilhetes:
        resultado.append({
            'id_bilhete': b['id_bilhete'],
            'numero': b['numero'],
            'rifa_nome': b['rifa_nome'],
            'rifa_id': b['id_rifa'],
            'premio': b['premio'],
            'data_compra': b['data_compra'].strftime('%Y-%m-%d %H:%M:%S') if b['data_compra'] else None,
            'data_sorteio': b['data_sorteio'].strftime('%Y-%m-%d %H:%M:%S') if b['data_sorteio'] else None,
            'valor': float(b['valor_bilhete']),
            'numero_sorteado': b['numero_sorteado'],
            'premiado': bool(b['premiado'])
        })
    
    print(f"📊 Retornando {len(resultado)} bilhetes. Premiados: {sum(1 for b in resultado if b['premiado'])}")
    return jsonify(resultado)