# routes/pagamento.py
from flask import Blueprint, request, session, jsonify
from models.reserva import Reserva
from models.bilhete import Bilhete
from models.pagamento import Pagamento

pagamento_bp = Blueprint('pagamento', __name__)

@pagamento_bp.route('/api/pagamentos/simular', methods=['POST'])
def simular_pagamento():
    # Verificar autenticação
    if 'usuario_id' not in session:
        return jsonify({'erro': 'Usuário não autenticado'}), 401
    
    data = request.get_json()
    reserva_id = data.get('reserva_id')
    metodo = data.get('metodo', 'pix')
    
    if not reserva_id:
        return jsonify({'erro': 'Reserva é obrigatória'}), 400
    
    # Verificar se a reserva existe e pertence ao usuário
    reserva = Reserva.get_by_id(reserva_id)
    
    if not reserva:
        return jsonify({'erro': 'Reserva não encontrada'}), 404
    
    if reserva['usuario_id'] != session['usuario_id']:
        return jsonify({'erro': 'Reserva não pertence ao usuário'}), 403
    
    if reserva['status'] != 'ativa':
        return jsonify({'erro': 'Reserva já foi processada ou expirou'}), 400
    
    # Verificar se ainda está dentro do prazo
    from datetime import datetime
    if reserva['data_expiracao'] < datetime.now():
        return jsonify({'erro': 'Reserva expirada'}), 400
    
    # Simular pagamento (sempre aprovado)
    valor_total = reserva['valor_bilhete'] * len(Reserva.get_ativas_por_usuario(session['usuario_id']))
    
    # Criar registro de pagamento
    pagamento_id = Pagamento.criar(
        reserva_id=reserva_id,
        usuario_id=session['usuario_id'],
        valor=valor_total,
        metodo=metodo
    )
    
    # Confirmar pagamento
    Reserva.converter_para_pago(reserva_id, session['usuario_id'])
    
    return jsonify({
        'sucesso': True,
        'mensagem': 'Pagamento simulado com sucesso!',
        'pagamento_id': pagamento_id,
        'bilhetes_comprados': []  # Pode buscar os números
    })

@pagamento_bp.route('/api/meus-bilhetes', methods=['GET'])
def get_meus_bilhetes():
    if 'usuario_id' not in session:
        return jsonify({'erro': 'Usuário não autenticado'}), 401
    
    bilhetes = Bilhete.get_meus_bilhetes(session['usuario_id'])
    
    # Agrupar por rifa
    resultado = []
    for b in bilhetes:
        resultado.append({
            'id_bilhete': b['id_bilhete'],
            'numero': b['numero'],
            'rifa_nome': b['rifa_nome'],
            'premio': b['premio'],
            'data_sorteio': b['data_sorteio'].strftime('%Y-%m-%d %H:%M:%S'),
            'valor': float(b['valor_bilhete']),
            'numero_sorteado': b['numero_sorteado'],
            'premiado': bool(b['premiado'])
        })
    
    return jsonify(resultado)