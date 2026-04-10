from flask import Flask, jsonify, request  
from flask_cors import CORS
from config import Config
import jwt
from routes.auth import auth_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# CORS configurado
CORS(app, origins=['http://localhost:5500', 'http://127.0.0.1:5500'], supports_credentials=True)

# Registrar blueprints
app.register_blueprint(auth_bp)

# Rota de teste para rifas (temporária)
@app.route('/api/rifas', methods=['GET'])
def listar_rifas():
    from utils.database import get_db
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id_rifa, nome, descricao, imagem, data_sorteio, valor_bilhete, premio, total_numeros FROM rifa WHERE status = "ativa" AND data_sorteio > NOW()')
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
            'data_sorteio': r['data_sorteio'].strftime('%Y-%m-%d %H:%M:%S'),
            'valor_bilhete': float(r['valor_bilhete']),
            'premio': r['premio'],
            'total_numeros': r['total_numeros']
        })
    return jsonify(resultado)

@app.route('/api/rifas/<int:id_rifa>/numeros', methods=['GET'])
def get_numeros(id_rifa):
    from utils.database import get_db
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT total_numeros FROM rifa WHERE id_rifa = %s', (id_rifa,))
    rifa = cursor.fetchone()
    if not rifa:
        return jsonify({'erro': 'Rifa não encontrada'}), 404
    
    cursor.execute('SELECT numero, status FROM bilhete WHERE rifa_id = %s', (id_rifa,))
    bilhetes = cursor.fetchall()
    cursor.close()
    conn.close()
    
    disponiveis = [b['numero'] for b in bilhetes if b['status'] == 'disponivel']
    reservados = [b['numero'] for b in bilhetes if b['status'] == 'reservado']
    pagos = [b['numero'] for b in bilhetes if b['status'] == 'pago']
    
    return jsonify({
        'total': rifa['total_numeros'],
        'disponiveis': disponiveis,
        'reservados': reservados,
        'pagos': pagos
    })
@app.route('/api/rifas/<int:id_rifa>', methods=['GET'])
def get_rifa(id_rifa):
    from utils.database import get_db
    conn = get_db()
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
        'data_sorteio': rifa['data_sorteio'].strftime('%Y-%m-%d %H:%M:%S'),
        'valor_bilhete': float(rifa['valor_bilhete']),
        'premio': rifa['premio'],
        'total_numeros': rifa['total_numeros']
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


@app.route('/api/admin/rifas', methods=['GET'])
def admin_listar_rifas():
    from utils.database import get_db
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT r.*, 
               COUNT(CASE WHEN b.status = 'pago' THEN 1 END) as vendidos
        FROM rifa r
        LEFT JOIN bilhete b ON r.id_rifa = b.rifa_id
        GROUP BY r.id_rifa
        ORDER BY r.id_rifa DESC
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
            'premio': r['premio'],
            'valor_bilhete': float(r['valor_bilhete']),
            'total_numeros': r['total_numeros'],
            'vendidos': r['vendidos'] or 0,
            'status': r['status'],
            'data_sorteio': r['data_sorteio'].strftime('%Y-%m-%d %H:%M:%S') if r['data_sorteio'] else None
        })
    return jsonify(resultado)
@app.route('/api/reservas/ativas', methods=['GET', 'OPTIONS'])
def get_reservas_ativas():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5500')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response, 200
    
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'erro': 'Token não fornecido'}), 401
    
    try:
        if token.startswith('Bearer '):
            token = token[7:]
        data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        current_user = data['usuario_id']
    except Exception as e:
        print(f"Erro no token: {e}")
        return jsonify({'erro': 'Token inválido'}), 401
    
    from utils.database import get_db
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Query corrigida - sem GROUP BY problemático
        cursor.execute('''
            SELECT 
                r.id_reserva, 
                r.data_expiracao, 
                rif.nome as rifa_nome, 
                rif.valor_bilhete,
                b.numero
            FROM reserva r
            INNER JOIN bilhete b ON r.id_reserva = b.reserva_id
            INNER JOIN rifa rif ON b.rifa_id = rif.id_rifa
            WHERE r.usuario_id = %s AND r.status = 'ativa' AND r.data_expiracao > NOW()
        ''', (current_user,))
        
        resultados = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Agrupar os números manualmente
        reservas_dict = {}
        for row in resultados:
            reserva_id = row['id_reserva']
            if reserva_id not in reservas_dict:
                reservas_dict[reserva_id] = {
                    'id_reserva': reserva_id,
                    'data_expiracao': row['data_expiracao'].strftime('%Y-%m-%d %H:%M:%S'),
                    'rifa_nome': row['rifa_nome'],
                    'numeros': [],
                    'valor_bilhete': float(row['valor_bilhete'])
                }
            reservas_dict[reserva_id]['numeros'].append(row['numero'])
        
        resultado = []
        for reserva in reservas_dict.values():
            resultado.append({
                'id_reserva': reserva['id_reserva'],
                'data_expiracao': reserva['data_expiracao'],
                'rifa_nome': reserva['rifa_nome'],
                'numeros': sorted(reserva['numeros']),
                'valor_total': float(reserva['valor_bilhete'] * len(reserva['numeros']))
            })
        
        response = jsonify(resultado)
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5500')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
        
    except Exception as e:
        print(f"Erro na query: {e}")
        return jsonify({'erro': str(e)}), 500
    
@app.route('/api/pagamentos/simular', methods=['POST', 'OPTIONS'])
def simular_pagamento():
    # Responder OPTIONS para CORS
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5500')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response, 200
    
    # Verificar token
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'erro': 'Token não fornecido'}), 401
    
    try:
        if token.startswith('Bearer '):
            token = token[7:]
        data = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        current_user = data['usuario_id']
    except Exception as e:
        print(f"Erro no token: {e}")
        return jsonify({'erro': 'Token inválido'}), 401
    
    data = request.get_json()
    reserva_id = data.get('reserva_id')
    metodo = data.get('metodo', 'pix')
    
    if not reserva_id:
        return jsonify({'erro': 'Reserva é obrigatória'}), 400
    
    from utils.database import get_db
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # Verificar se a reserva pertence ao usuário
    cursor.execute('''
        SELECT r.id_reserva, r.data_expiracao, r.status
        FROM reserva r
        WHERE r.id_reserva = %s AND r.usuario_id = %s AND r.status = 'ativa'
    ''', (reserva_id, current_user))
    
    reserva = cursor.fetchone()
    
    if not reserva:
        cursor.close()
        conn.close()
        return jsonify({'erro': 'Reserva não encontrada'}), 404
    
    # Verificar se não expirou
    from datetime import datetime
    if reserva['data_expiracao'] < datetime.now():
        cursor.close()
        conn.close()
        return jsonify({'erro': 'Reserva expirada'}), 400
    
    # Atualizar reserva para convertida
    cursor.execute('UPDATE reserva SET status = "convertida" WHERE id_reserva = %s', (reserva_id,))
    
    # Atualizar bilhetes para pago
    cursor.execute('''
        UPDATE bilhete 
        SET status = 'pago', usuario_id = %s, data_compra = NOW()
        WHERE reserva_id = %s
    ''', (current_user, reserva_id))
    
    # Calcular valor total
    cursor.execute('''
        SELECT SUM(rif.valor_bilhete) as total
        FROM bilhete b
        INNER JOIN rifa rif ON b.rifa_id = rif.id_rifa
        WHERE b.reserva_id = %s
    ''', (reserva_id,))
    
    total_result = cursor.fetchone()
    valor_total = float(total_result['total']) if total_result and total_result['total'] else 0
    
    # Registrar pagamento
    cursor.execute('''
        INSERT INTO pagamento (reserva_id, usuario_id, metodo, status, valor)
        VALUES (%s, %s, %s, 'aprovado', %s)
    ''', (reserva_id, current_user, metodo, valor_total))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    response = jsonify({
        'sucesso': True,
        'mensagem': f'Pagamento simulado com {metodo} realizado com sucesso!'
    })
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5500')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response
    
@app.route('/api/admin/usuarios', methods=['GET'])
def admin_listar_usuarios():
    from utils.database import get_db
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id_usuario, nome, email, tipo, status, data_cadastro FROM usuario ORDER BY id_usuario DESC')
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()
    
    for u in usuarios:
        u['data_cadastro'] = u['data_cadastro'].strftime('%Y-%m-%d %H:%M:%S') if u['data_cadastro'] else None
    
    return jsonify(usuarios)

@app.route('/api/admin/rifas', methods=['POST'])
def admin_criar_rifa():
    from utils.database import get_db
    data = request.get_json()
    
    nome = data.get('nome')
    descricao = data.get('descricao')
    imagem = data.get('imagem', '')
    data_sorteio = data.get('data_sorteio')
    valor_bilhete = data.get('valor_bilhete')
    premio = data.get('premio')
    total_numeros = data.get('total_numeros')
    
    if not all([nome, descricao, data_sorteio, valor_bilhete, premio, total_numeros]):
        return jsonify({'erro': 'Todos os campos são obrigatórios'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO rifa (nome, descricao, imagem, data_inicio, data_sorteio, valor_bilhete, premio, total_numeros, status)
            VALUES (%s, %s, %s, NOW(), %s, %s, %s, %s, 'ativa')
        ''', (nome, descricao, imagem, data_sorteio, valor_bilhete, premio, total_numeros))
        
        rifa_id = cursor.lastrowid
        
        # Criar bilhetes
        for i in range(1, total_numeros + 1):
            cursor.execute('INSERT INTO bilhete (numero, status, rifa_id) VALUES (%s, "disponivel", %s)', (i, rifa_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'sucesso': True, 'mensagem': 'Rifa criada', 'rifa_id': rifa_id}), 201
        
    except Exception as e:
        conn.close()
        return jsonify({'erro': str(e)}), 500

@app.route('/api/admin/rifas/<int:rifa_id>/sorteio', methods=['POST'])
def admin_realizar_sorteio(rifa_id):
    from utils.database import get_db
    import random
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # Buscar bilhetes pagos
    cursor.execute('SELECT id_bilhete, numero, usuario_id FROM bilhete WHERE rifa_id = %s AND status = "pago"', (rifa_id,))
    bilhetes = cursor.fetchall()
    
    if not bilhetes:
        cursor.close()
        conn.close()
        return jsonify({'erro': 'Não há bilhetes vendidos'}), 400
    
    # Sortear
    vencedor = random.choice(bilhetes)
    
    # Registrar sorteio
    cursor.execute('''
        INSERT INTO sorteio (data_sorteio, numero_sorteado, rifa_id, bilhete_vencedor_id)
        VALUES (NOW(), %s, %s, %s)
    ''', (vencedor['numero'], rifa_id, vencedor['id_bilhete']))
    
    # Atualizar status da rifa
    cursor.execute('UPDATE rifa SET status = "finalizada" WHERE id_rifa = %s', (rifa_id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({
        'sucesso': True,
        'vencedor': {
            'numero': vencedor['numero'],
            'bilhete_id': vencedor['id_bilhete']
        }
    })

if __name__ == '__main__':
    print("🚀 Servidor rodando em http://localhost:5000")
    app.run(debug=True, port=5000)