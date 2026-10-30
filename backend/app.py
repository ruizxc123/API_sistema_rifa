from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
import logging

from flask import Flask, jsonify, request
from flask_cors import CORS

from config import Config
from middleware.auth import admin_required
from routes.auth import auth_bp
from utils.database import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Config.validate()
app = Flask(__name__)
app.config["SECRET_KEY"] = Config.SECRET_KEY
CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=False)
app.register_blueprint(auth_bp)


def _error_unavailable():
    return jsonify({"erro": "Serviço temporariamente indisponível."}), 503


def _iso(value):
    return value.isoformat() if value else None


@app.get("/api/rifas")
def listar_rifas():
    conn = get_db()
    if conn is None:
        return _error_unavailable()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT id_rifa, nome, descricao, imagem, data_sorteio,
                      valor_bilhete, premio, total_numeros
               FROM rifa
               WHERE status = 'ativa' AND data_sorteio > UTC_TIMESTAMP()
               ORDER BY data_sorteio ASC"""
        )
        rows = cursor.fetchall()
        cursor.close()
    finally:
        conn.close()
    return jsonify(
        [
            {
                "id_rifa": row["id_rifa"],
                "nome": row["nome"],
                "descricao": row["descricao"],
                "imagem": row["imagem"] or "",
                "data_sorteio": _iso(row["data_sorteio"]),
                "valor_bilhete": float(row["valor_bilhete"]),
                "premio": row["premio"],
                "total_numeros": row["total_numeros"],
            }
            for row in rows
        ]
    )


@app.get("/api/rifas/<int:rifa_id>/numeros")
def get_numeros(rifa_id):
    conn = get_db()
    if conn is None:
        return _error_unavailable()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT total_numeros FROM rifa WHERE id_rifa = %s AND status = 'ativa'",
            (rifa_id,),
        )
        rifa = cursor.fetchone()
        if not rifa:
            cursor.close()
            return jsonify({"erro": "Campanha não encontrada."}), 404
        cursor.execute(
            "SELECT numero, status FROM bilhete WHERE rifa_id = %s ORDER BY numero",
            (rifa_id,),
        )
        tickets = cursor.fetchall()
        cursor.close()
    finally:
        conn.close()
    return jsonify(
        {
            "total": rifa["total_numeros"],
            "disponiveis": [item["numero"] for item in tickets if item["status"] == "disponivel"],
            "reservados": [item["numero"] for item in tickets if item["status"] == "reservado"],
            "pagos": [item["numero"] for item in tickets if item["status"] == "pago"],
        }
    )


@app.get("/api/rifas/<int:rifa_id>")
def get_rifa(rifa_id):
    conn = get_db()
    if conn is None:
        return _error_unavailable()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT id_rifa, nome, descricao, imagem, data_sorteio,
                      valor_bilhete, premio, total_numeros
               FROM rifa WHERE id_rifa = %s AND status = 'ativa'""",
            (rifa_id,),
        )
        row = cursor.fetchone()
        cursor.close()
    finally:
        conn.close()
    if not row:
        return jsonify({"erro": "Campanha não encontrada."}), 404
    return jsonify(
        {
            "id_rifa": row["id_rifa"],
            "nome": row["nome"],
            "descricao": row["descricao"],
            "imagem": row["imagem"],
            "data_sorteio": _iso(row["data_sorteio"]),
            "valor_bilhete": float(row["valor_bilhete"]),
            "premio": row["premio"],
            "total_numeros": row["total_numeros"],
        }
    )


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api/admin/rifas")
@admin_required
def admin_listar_rifas():
    conn = get_db()
    if conn is None:
        return _error_unavailable()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT r.id_rifa, r.nome, r.descricao, r.premio, r.valor_bilhete,
                      r.total_numeros, r.status, r.data_sorteio,
                      COALESCE(b.vendidos, 0) AS vendidos
               FROM rifa r
               LEFT JOIN (
                   SELECT rifa_id, COUNT(*) AS vendidos
                   FROM bilhete WHERE status = 'pago' GROUP BY rifa_id
               ) b ON b.rifa_id = r.id_rifa
               ORDER BY r.id_rifa DESC"""
        )
        rows = cursor.fetchall()
        cursor.close()
    finally:
        conn.close()
    return jsonify(
        [
            {
                **row,
                "valor_bilhete": float(row["valor_bilhete"]),
                "data_sorteio": _iso(row["data_sorteio"]),
            }
            for row in rows
        ]
    )


@app.get("/api/admin/usuarios")
@admin_required
def admin_listar_usuarios():
    conn = get_db()
    if conn is None:
        return _error_unavailable()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT id_usuario, nome, email, tipo, status, data_cadastro
               FROM usuario ORDER BY id_usuario DESC"""
        )
        rows = cursor.fetchall()
        cursor.close()
    finally:
        conn.close()
    return jsonify([{**row, "data_cadastro": _iso(row["data_cadastro"])} for row in rows])


@app.post("/api/admin/rifas")
@admin_required
def admin_criar_rifa():
    data = request.get_json(silent=True) or {}
    nome = str(data.get("nome", "")).strip()
    descricao = str(data.get("descricao", "")).strip()
    premio = str(data.get("premio", "")).strip()
    imagem = str(data.get("imagem", "")).strip()
    try:
        quantidade = int(data.get("total_numeros"))
        valor = Decimal(str(data.get("valor_bilhete")))
        data_sorteio = datetime.fromisoformat(str(data.get("data_sorteio", "")).replace("Z", "+00:00"))
        if data_sorteio.tzinfo is not None:
            data_sorteio = data_sorteio.astimezone(timezone.utc).replace(tzinfo=None)
    except (TypeError, ValueError, InvalidOperation):
        return jsonify({"erro": "Quantidade, valor ou data inválidos."}), 400

    if not nome or len(nome) > 150 or not descricao or not premio:
        return jsonify({"erro": "Nome, descrição e prêmio são obrigatórios."}), 400
    if len(imagem) > 500 or not valor.is_finite() or valor < 0 or not 1 <= quantidade <= 50000:
        return jsonify({"erro": "Valor, imagem ou quantidade fora dos limites aceitos."}), 400
    if data_sorteio.replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc):
        return jsonify({"erro": "A data precisa estar no futuro."}), 400

    conn = get_db()
    if conn is None:
        return _error_unavailable()
    try:
        conn.start_transaction()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO rifa
               (nome, descricao, imagem, data_inicio, data_sorteio,
                valor_bilhete, premio, total_numeros, status)
               VALUES (%s, %s, %s, UTC_TIMESTAMP(), %s, %s, %s, %s, 'inativa')""",
            (nome, descricao, imagem, data_sorteio, valor, premio, quantidade),
        )
        rifa_id = cursor.lastrowid
        cursor.executemany(
            "INSERT INTO bilhete (numero, status, rifa_id) VALUES (%s, 'disponivel', %s)",
            [(number, rifa_id) for number in range(1, quantidade + 1)],
        )
        conn.commit()
        cursor.close()
    except Exception:
        conn.rollback()
        logger.exception("Falha ao criar campanha inativa.")
        return jsonify({"erro": "Não foi possível criar a campanha."}), 500
    finally:
        conn.close()
    return jsonify({"sucesso": True, "mensagem": "Campanha criada como inativa; exige análise antes de publicação.", "rifa_id": rifa_id}), 201


@app.post("/api/pagamentos/simular")
def pagamento_simulado_desativado():
    return jsonify({"erro": "Pagamento simulado foi desativado. Nenhum pagamento foi processado."}), 410


@app.post("/api/admin/rifas/<int:rifa_id>/sorteio")
@admin_required
def sorteio_desativado(rifa_id):
    return jsonify({"erro": "Sorteios estão desativados até a validação jurídica e técnica do método aplicável."}), 409


if __name__ == "__main__":
    app.run(host="127.0.0.1", debug=False, port=5000)
