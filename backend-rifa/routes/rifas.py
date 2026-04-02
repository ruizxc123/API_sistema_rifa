# routes/rifas.py
from flask import Blueprint, jsonify
from models.rifa import Rifa

rifas_bp = Blueprint('rifas', __name__)

@rifas_bp.route('/api/rifas', methods=['GET'])
def listar_rifas():
    rifas = Rifa.listar_ativas()
    
    # Formatar dados
    resultado = []
    for rifa in rifas:
        resultado.append({
            'id_rifa': rifa['id_rifa'],
            'nome': rifa['nome'],
            'descricao': rifa['descricao'],
            'imagem': rifa['imagem'],
            'data_inicio': rifa['data_inicio'].strftime('%Y-%m-%d %H:%M:%S'),
            'data_sorteio': rifa['data_sorteio'].strftime('%Y-%m-%d %H:%M:%S'),
            'valor_bilhete': float(rifa['valor_bilhete']),
            'premio': rifa['premio'],
            'total_numeros': rifa['total_numeros']
        })
    
    return jsonify(resultado)

@rifas_bp.route('/api/rifas/<int:id_rifa>', methods=['GET'])
def get_rifa(id_rifa):
    rifa = Rifa.buscar_por_id(id_rifa)
    
    if not rifa:
        return jsonify({'erro': 'Rifa não encontrada'}), 404
    
    return jsonify({
        'id_rifa': rifa['id_rifa'],
        'nome': rifa['nome'],
        'descricao': rifa['descricao'],
        'imagem': rifa['imagem'],
        'data_inicio': rifa['data_inicio'].strftime('%Y-%m-%d %H:%M:%S'),
        'data_sorteio': rifa['data_sorteio'].strftime('%Y-%m-%d %H:%M:%S'),
        'valor_bilhete': float(rifa['valor_bilhete']),
        'premio': rifa['premio'],
        'total_numeros': rifa['total_numeros']
    })

@rifas_bp.route('/api/rifas/<int:id_rifa>/numeros', methods=['GET'])
def get_numeros_rifa(id_rifa):
    rifa = Rifa.buscar_por_id(id_rifa)
    
    if not rifa:
        return jsonify({'erro': 'Rifa não encontrada'}), 404
    
    numeros_status = Rifa.get_numeros_status(id_rifa)
    
    return jsonify({
        'total': rifa['total_numeros'],
        'disponiveis': numeros_status['disponiveis'],
        'reservados': numeros_status['reservados'],
        'pagos': numeros_status['pagos']
    })