# app.py
from flask import Flask, session, jsonify
from flask_cors import CORS
from config import Config

# Importar blueprints
from routes.auth import auth_bp
from routes.rifas import rifas_bp
from routes.reservas import reservas_bp
from routes.pagamento import pagamento_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['SESSION_TYPE'] = 'filesystem'

# Configurar CORS para permitir requisições do frontend
CORS(app, supports_credentials=True, origins=['http://localhost:5500', 'http://127.0.0.1:5500', 'http://localhost:3000'])

# Registrar blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(rifas_bp)
app.register_blueprint(reservas_bp)
app.register_blueprint(pagamento_bp)

# Rota de teste
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'API está funcionando!'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)