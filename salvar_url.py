
from flask import Flask, request, redirect
import cloudinary
import cloudinary.uploader
import mysql.connector
import uuid

app = Flask(__name__)

# CLOUDINARY
cloudinary.config(
    cloud_name="",
    api_key="",
    api_secret=""
)

# MYSQL
conexao = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="rifa_online"
)

cursor = conexao.cursor(dictionary=True)

# 🔥 FORMULÁRIO
@app.route("/")
def index():
    return '''
    <h2>Criar Rifa</h2>
    <form method="POST" action="/upload" enctype="multipart/form-data">
        Nome: <input type="text" name="nome" required><br>
        Descrição: <input type="text" name="descricao" required><br>
        Imagem: <input type="file" name="imagem" required><br>
        Data início: <input type="datetime-local" name="data_inicio" required><br>
        Data sorteio: <input type="datetime-local" name="data_sorteio" required><br>
        Valor: <input type="number" step="0.01" name="valor" required><br>
        Prêmio: <input type="text" name="premio" required><br>
        Total números: <input type="number" name="total" required><br>
        <button type="submit">Criar</button>
    </form>
    <br>
    <a href="/rifas">Ver Rifas</a>
    '''

# 🔥 UPLOAD + SALVAR
@app.route("/upload", methods=["POST"])
def upload():
    try:
        if "imagem" not in request.files:
            return "Erro: envie uma imagem"

        file = request.files["imagem"]

        if file.filename == "":
            return "Erro: arquivo inválido"

        # 🔥 UPLOAD COM PRESET (SEM ERRO DE PERMISSÃO)
        resultado = cloudinary.uploader.upload(
            file,
            upload_preset="rifa_upload"
        )

        url_imagem = resultado["secure_url"]

        # 🔥 PEGAR DADOS
        nome = request.form.get("nome")
        descricao = request.form.get("descricao")
        data_inicio = request.form.get("data_inicio")
        data_sorteio = request.form.get("data_sorteio")
        valor = request.form.get("valor")
        premio = request.form.get("premio")
        total = request.form.get("total")

        # 🔥 VALIDAÇÃO
        if not all([nome, descricao, data_inicio, data_sorteio, valor, premio, total]):
            return "Erro: preencha todos os campos"

        # 🔥 CORRIGIR DATA
        data_inicio = data_inicio.replace("T", " ") + ":00"
        data_sorteio = data_sorteio.replace("T", " ") + ":00"

        # 🔥 SALVAR NO BANCO
        cursor.execute("""
        INSERT INTO rifa 
        (nome, descricao, imagem, data_inicio, data_sorteio, valor_bilhete, premio, total_numeros, status)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            nome,
            descricao,
            url_imagem,
            data_inicio,
            data_sorteio,
            valor,
            premio,
            total,
            "ativa"
        ))

        conexao.commit()

        return redirect("/rifas")

    except Exception as e:
        return f"Erro: {str(e)}"

# 🔥 LISTAR RIFAS
@app.route("/rifas")
def listar():
    cursor.execute("SELECT * FROM rifa")
    rifas = cursor.fetchall()

    html = "<h2>Rifas</h2>"

    for r in rifas:
        html += f"""
        <div style='border:1px solid #ccc; margin:10px; padding:10px'>
            <h3>{r['nome']}</h3>
            <img src="{r['imagem']}" width="200"><br>
            <p>{r['descricao']}</p>
            <p>Valor: R$ {r['valor_bilhete']}</p>
            <p>Prêmio: {r['premio']}</p>
            <p>Status: {r['status']}</p>
        </div>
        """

    html += "<br><a href='/'>Voltar</a>"
    return html

if __name__ == "__main__":
    app.run(debug=True)