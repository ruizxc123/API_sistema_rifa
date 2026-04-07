from flask import Flask, request, jsonify, send_from_directory
import os
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'imagens_enviadas'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def receber_imagem():
    # Pega a imagem enviada com o nome "imagem"
    arquivo = request.files['imagem']
    
    # Cria um nome único (ex: a1b2c3.jpg)
    extensao = arquivo.filename.split('.')[-1]
    nome_unico = f"{uuid.uuid4().hex}.{extensao}"
    caminho = os.path.join(UPLOAD_FOLDER, nome_unico)
    
    # Salva a imagem no servidor
    arquivo.save(caminho)
    
    # Monta a URL pública da imagem
    url_da_imagem = f"http://127.0.0.1:5000/imagens/{nome_unico}"
    
    # Retorna APENAS o texto com a URL (não a imagem!)
    return jsonify({'url': url_da_imagem})

@app.route('/imagens/<nome_arquivo>')
def mostrar_imagem(nome_arquivo):
    # Rota que serve a imagem quando alguém acessa a URL
    return send_from_directory(UPLOAD_FOLDER, nome_arquivo)

if __name__ == '__main__':
    app.run(debug=True)