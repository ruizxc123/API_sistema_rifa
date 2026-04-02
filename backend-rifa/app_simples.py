# app_simples.py
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({'mensagem': 'API funcionando!'})

@app.route('/api/rifas')
def rifas():
    return jsonify([
        {'id': 1, 'nome': 'Nintendo Switch', 'valor': 10.00},
        {'id': 2, 'nome': 'PlayStation 5', 'valor': 15.00}
    ])

if __name__ == '__main__':
    app.run(debug=True, port=5000)