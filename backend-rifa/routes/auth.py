# routes/auth.py
from flask import Blueprint, request, session, jsonify
from models.usuario import Usuario

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')
    
    if not email or not senha:
        return jsonify({'erro': 'Email e senha são obrigatórios'}), 400
    
    usuario = Usuario.autenticar(email, senha)
    
    if not usuario:
        return jsonify({'erro': 'Email ou senha inválidos'}), 401
    
    # Salvar na sessão
    session['usuario_id'] = usuario['id_usuario']
    session['usuario_nome'] = usuario['nome']
    
    return jsonify({
        'sucesso': True,
        'mensagem': 'Login realizado com sucesso',
        'usuario': {
            'id_usuario': usuario['id_usuario'],
            'nome': usuario['nome'],
            'email': usuario['email']
        }
    })

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'sucesso': True, 'mensagem': 'Logout realizado'})

@auth_bp.route('/api/session', methods=['GET'])
def get_session():
    if 'usuario_id' in session:
        usuario = Usuario.buscar_por_id(session['usuario_id'])
        return jsonify({
            'usuario_id': session['usuario_id'],
            'usuario': usuario
        })
    
    return jsonify({'usuario_id': None})

@auth_bp.route('/api/usuarios/registrar', methods=['POST'])
def registrar():
    data = request.get_json()
    
    nome = data.get('nome')
    email = data.get('email')
    cpf = data.get('cpf')
    telefone = data.get('telefone')
    senha = data.get('senha')
    
    # Validações básicas
    if not all([nome, email, cpf, telefone, senha]):
        return jsonify({'erro': 'Todos os campos são obrigatórios'}), 400
    
    # Verificar se email já existe
    usuario_existente = Usuario.buscar_por_email(email)
    if usuario_existente:
        return jsonify({'erro': 'Email já cadastrado'}), 400
    
    # Criar usuário
    try:
        usuario_id = Usuario.criar(nome, email, cpf, telefone, senha)
        return jsonify({
            'sucesso': True,
            'mensagem': 'Usuário cadastrado com sucesso',
            'usuario_id': usuario_id
        }), 201
    except Exception as e:
        return jsonify({'erro': f'Erro ao cadastrar: {str(e)}'}), 500