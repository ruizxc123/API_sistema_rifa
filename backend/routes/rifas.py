from flask import Blueprint, jsonify
from utils.database import get_db

rifas_bp = Blueprint('rifas', __name__)

@rifas_bp.route('/api/rifas', methods=['GET'])
def listar_rifas():
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

@rifas_bp.route('/api/rifas/<int:id_rifa>/numeros', methods=['GET'])
def get_numeros(id_rifa):
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
    
    return jsonify({'total': rifa['total_numeros'], 'disponiveis': disponiveis, 'reservados': reservados, 'pagos': pagos})