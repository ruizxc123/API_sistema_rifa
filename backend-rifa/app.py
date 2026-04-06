from flask import Flask, jsonify, request
from flask_cors import CORS
from config import Config
import mysql.connector
from mysql.connector import Error
import hashlib
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# CORS liberado para todos (mais simples)
CORS(app, origins='*')

# Configurações do MySQL
DB_CONFIG = {
    'host': Config.MYSQL_HOST,
    'user': Config.MYSQL_USER,
    'password': Config.MYSQL_PASSWORD,
    'database': Config.MYSQL_DATABASE,
    'autocommit': True
}

def get_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"❌ Erro ao conectar ao MySQL: {e}")
        return None

# Decorator para verificar token
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'erro': 'Token não fornecido'}), 401
        
        try:
            # Remover 'Bearer ' do token
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = data['usuario_id']
        except:
            return jsonify({'erro': 'Token inválido ou expirado'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# ========== ROTAS ==========

@app.route('/')
def index():
    return jsonify({
        'mensagem': 'API Rifa Online',
        'status': 'online',
        'versao': '2.0'
    })

@app.route('/api/health', methods=['GET'])
def health():
    conn = get_db()
    if conn:
        conn.close()
        return jsonify({'status': 'ok', 'database': 'conectado'})
    return jsonify({'status': 'erro', 'database': 'desconectado'}), 500

# LOGIN - retorna token
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')
    
    if not email or not senha:
        return jsonify({'erro': 'Email e senha são obrigatórios'}), 400
    
    senha_hash = hashlib.md5(senha.encode()).hexdigest()
    
    conn = get_db()
    if not conn:
        return jsonify({'erro': 'Erro de conexão com o banco'}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT id_usuario, nome, email FROM usuario 
        WHERE email = %s AND senha = %s AND status = 1
    ''', (email, senha_hash))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not usuario:
        return jsonify({'erro': 'Email ou senha inválidos'}), 401
    
    # Gerar token JWT (válido por 24 horas)
    token = jwt.encode({
        'usuario_id': usuario['id_usuario'],
        'usuario_nome': usuario['nome'],
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'sucesso': True,
        'mensagem': 'Login realizado com sucesso',
        'token': token,
        'usuario': {
            'id_usuario': usuario['id_usuario'],
            'nome': usuario['nome'],
            'email': usuario['email']
        }
    })

# VERIFICAR SESSÃO (via token)
@app.route('/api/session', methods=['GET'])
def get_session():
    token = request.headers.get('Authorization')
    
    if not token:
        return jsonify({'usuario_id': None})
    
    try:
        if token.startswith('Bearer '):
            token = token[7:]
        
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return jsonify({
            'usuario_id': data['usuario_id'],
            'usuario': {'nome': data['usuario_nome']}
        })
    except:
        return jsonify({'usuario_id': None})

# CADASTRO
@app.route('/api/usuarios/registrar', methods=['POST'])
def registrar():
    data = request.get_json()
    
    nome = data.get('nome')
    email = data.get('email')
    cpf = data.get('cpf')
    telefone = data.get('telefone')
    senha = data.get('senha')
    
    if not all([nome, email, cpf, telefone, senha]):
        return jsonify({'erro': 'Todos os campos são obrigatórios'}), 400
    
    senha_hash = hashlib.md5(senha.encode()).hexdigest()
    
    conn = get_db()
    if not conn:
        return jsonify({'erro': 'Erro de conexão com o banco'}), 500
    
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO usuario (nome, email, cpf, telefone, senha)
            VALUES (%s, %s, %s, %s, %s)
        ''', (nome, email, cpf, telefone, senha_hash))
        conn.commit()
        usuario_id = cursor.lastrowid
        cursor.close()
        conn.close()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Usuário cadastrado com sucesso',
            'usuario_id': usuario_id
        }), 201
    except Error as e:
        conn.close()
        if 'Duplicate entry' in str(e):
            return jsonify({'erro': 'Email ou CPF já cadastrado'}), 400
        return jsonify({'erro': str(e)}), 500

# RIFAS (público)
@app.route('/api/rifas', methods=['GET'])
def listar_rifas():
    conn = get_db()
    if not conn:
        return jsonify({'erro': 'Erro de conexão com o banco'}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT id_rifa, nome, descricao, imagem, data_sorteio, 
               valor_bilhete, premio, total_numeros
        FROM rifa WHERE status = 'ativa' AND data_sorteio > NOW()
    ''')
    rifas = cursor.fetchall()
    cursor.close()
    conn.close()
    
    resultado = []
    for r in rifas:
        resultado.append({
            'id_rifa': r['id_rifa'],
            'nome': r['nome'],
            'descricao': r['descricao'],
            'imagem': r['imagem'] or '',
            'data_sorteio': r['data_sorteio'].strftime('%Y-%m-%d %H:%M:%S') if r['data_sorteio'] else None,
            'valor_bilhete': float(r['valor_bilhete']),
            'premio': r['premio'],
            'total_numeros': r['total_numeros']
        })
    
    return jsonify(resultado)

@app.route('/api/rifas/<int:id_rifa>', methods=['GET'])
def get_rifa(id_rifa):
    conn = get_db()
    if not conn:
        return jsonify({'erro': 'Erro de conexão com o banco'}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM rifa WHERE id_rifa = %s', (id_rifa,))
    rifa = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not rifa:
        return jsonify({'erro': 'Rifa não encontrada'}), 404
    
    return jsonify({
        'id_rifa': rifa['id_rifa'],
        'nome': rifa['nome'],
        'descricao': rifa['descricao'],
        'imagem': rifa['imagem'],
        'data_sorteio': rifa['data_sorteio'].strftime('%Y-%m-%d %H:%M:%S') if rifa['data_sorteio'] else None,
        'valor_bilhete': float(rifa['valor_bilhete']),
        'premio': rifa['premio'],
        'total_numeros': rifa['total_numeros']
    })

@app.route('/api/rifas/<int:id_rifa>/numeros', methods=['GET'])
def get_numeros_rifa(id_rifa):
    conn = get_db()
    if not conn:
        return jsonify({'erro': 'Erro de conexão com o banco'}), 500
    
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute('SELECT total_numeros FROM rifa WHERE id_rifa = %s', (id_rifa,))
    rifa = cursor.fetchone()
    
    if not rifa:
        cursor.close()
        conn.close()
        return jsonify({'erro': 'Rifa não encontrada'}), 404
    
    cursor.execute('SELECT numero, status FROM bilhete WHERE rifa_id = %s', (id_rifa,))
    bilhetes = cursor.fetchall()
    cursor.close()
    conn.close()
    
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
    
    return jsonify({
        'total': rifa['total_numeros'],
        'disponiveis': disponiveis,
        'reservados': reservados,
        'pagos': pagos
    })

if __name__ == '__main__':
    print("🚀 Servidor rodando em http://localhost:5000")
    app.run(debug=True, port=5000)