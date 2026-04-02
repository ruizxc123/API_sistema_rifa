# routes/reservas.py
from flask import Blueprint, request, session, jsonify
from models.reserva import Reserva
from models.bilhete import Bilhete
from models.rifa import Rifa

reservas_bp = Blueprint('reservas', __name__)

@reservas_bp.route('/api/reservas/criar', methods=['POST'])
def criar_reserva():
    # Verificar autenticação
    if 'usuario_id' not in session:
        return jsonify({'erro': 'Usuário não autenticado'}), 401
    
    data = request.get_json()
    rifa_id = data.get('rifa_id')
    numeros = data.get('numeros')
    
    if not rifa_id or not numeros or len(numeros) == 0:
        return jsonify({'erro': 'Rifa e números são obrigatórios'}), 400
    
    # Verificar disponibilidade dos números
    disponivel, indisponiveis = Bilhete.verificar_disponibilidade(rifa_id, numeros)
    
    if not disponivel:
        return jsonify({
            'erro': 'Alguns números não estão disponíveis',
            'indisponiveis': indisponiveis
        }), 400
    
    # Criar reserva
    reserva = Reserva.criar(
        usuario_id=session['usuario_id'],
        rifa_id=rifa_id,
        numeros=numeros
    )
    
    return jsonify(reserva), 201

@reservas_bp.route('/api/reservas/ativas', methods=['GET'])
def get_reservas_ativas():
    if 'usuario_id' not in session:
        return jsonify({'erro': 'Usuário não autenticado'}), 401
    
    reservas = Reserva.get_ativas_por_usuario(session['usuario_id'])
    return jsonify(reservas)

@reservas_bp.route('/api/reservas/<int:reserva_id>/cancelar', methods=['DELETE'])
def cancelar_reserva(reserva_id):
    if 'usuario_id' not in session:
        return jsonify({'erro': 'Usuário não autenticado'}), 401
    
    sucesso = Reserva.cancelar(reserva_id, session['usuario_id'])
    
    if not sucesso:
        return jsonify({'erro': 'Reserva não encontrada ou já expirada'}), 404
    
    return jsonify({'sucesso': True, 'mensagem': 'Reserva cancelada'})