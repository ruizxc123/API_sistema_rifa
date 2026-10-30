from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import re

import jwt
from flask import Blueprint, current_app, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from middleware.auth import token_required
from utils.database import get_db

auth_bp = Blueprint("auth", __name__)


def _json_body():
    return request.get_json(silent=True) or {}


def _verify_and_upgrade_password(user_id, supplied, stored):
    if not isinstance(stored, str):
        return False
    if len(stored) == 32 and re.fullmatch(r"[0-9a-fA-F]{32}", stored):
        legacy_hash = hashlib.md5(supplied.encode("utf-8")).hexdigest()
        legacy_double_hash = hashlib.md5(legacy_hash.encode("ascii")).hexdigest()
        if not (
            hmac.compare_digest(legacy_hash.lower(), stored.lower())
            or hmac.compare_digest(legacy_double_hash.lower(), stored.lower())
        ):
            return False
        conn = get_db()
        if conn is None:
            return False
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE usuario SET senha = %s WHERE id_usuario = %s AND senha = %s",
                (generate_password_hash(supplied), user_id, stored),
            )
            conn.commit()
            cursor.close()
        finally:
            conn.close()
        return True
    try:
        return check_password_hash(stored, supplied)
    except (ValueError, TypeError):
        return False


@auth_bp.post("/api/login")
def login():
    data = _json_body()
    email = str(data.get("email", "")).strip().lower()
    senha = data.get("senha")
    if not email or not isinstance(senha, str) or not senha:
        return jsonify({"erro": "Email e senha são obrigatórios."}), 400

    conn = get_db()
    if conn is None:
        return jsonify({"erro": "Serviço temporariamente indisponível."}), 503
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_usuario, nome, email, tipo, status, senha FROM usuario WHERE email = %s",
            (email,),
        )
        user = cursor.fetchone()
        cursor.close()
    finally:
        conn.close()

    if not user or not user.get("status") or not _verify_and_upgrade_password(
        user["id_usuario"], senha, user["senha"]
    ):
        return jsonify({"erro": "Email ou senha inválidos."}), 401

    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "sub": str(user["id_usuario"]),
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(hours=1)).timestamp()),
            "iss": "api-sistema-rifa",
            "aud": "api-sistema-rifa-client",
        },
        current_app.config["SECRET_KEY"],
        algorithm="HS256",
    )
    return jsonify(
        {
            "sucesso": True,
            "token": token,
            "usuario": {
                "id_usuario": user["id_usuario"],
                "nome": user["nome"],
                "email": user["email"],
                "tipo": user["tipo"],
            },
        }
    )


@auth_bp.post("/api/usuarios/registrar")
def registrar():
    data = _json_body()
    nome = str(data.get("nome", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    cpf = re.sub(r"\D", "", str(data.get("cpf", "")))
    telefone = str(data.get("telefone", "")).strip()
    senha = data.get("senha")

    if not nome or len(nome) > 150 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        return jsonify({"erro": "Nome ou email inválido."}), 400
    if len(cpf) != 11 or not telefone or len(telefone) > 20:
        return jsonify({"erro": "CPF ou telefone inválido."}), 400
    if not isinstance(senha, str) or len(senha) < 12 or len(senha) > 256:
        return jsonify({"erro": "A senha deve ter entre 12 e 256 caracteres."}), 400

    conn = get_db()
    if conn is None:
        return jsonify({"erro": "Serviço temporariamente indisponível."}), 503
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuario (nome, email, cpf, telefone, senha, tipo) VALUES (%s, %s, %s, %s, %s, 'normal')",
            (nome, email, cpf, telefone, generate_password_hash(senha)),
        )
        conn.commit()
        user_id = cursor.lastrowid
        cursor.close()
    except Exception:
        conn.rollback()
        return jsonify({"erro": "Não foi possível concluir o cadastro. Confira os dados informados."}), 409
    finally:
        conn.close()
    return jsonify({"sucesso": True, "mensagem": "Usuário cadastrado.", "usuario_id": user_id}), 201


@auth_bp.get("/api/session")
@token_required
def get_session(current_user):
    conn = get_db()
    if conn is None:
        return jsonify({"erro": "Serviço temporariamente indisponível."}), 503
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id_usuario, nome, email, tipo FROM usuario WHERE id_usuario = %s AND status = 1",
            (current_user,),
        )
        user = cursor.fetchone()
        cursor.close()
    finally:
        conn.close()
    if not user:
        return jsonify({"usuario_id": None}), 401
    return jsonify({"usuario_id": user["id_usuario"], "usuario": user})


@auth_bp.post("/api/reservas/criar")
@token_required
def criar_reserva(current_user):
    return jsonify(
        {"erro": "Reservas e venda de números estão desativadas até a validação jurídica e regulatória do modelo."}
    ), 409


@auth_bp.get("/api/reservas/ativas")
@token_required
def get_reservas_ativas(current_user):
    conn = get_db()
    if conn is None:
        return jsonify({"erro": "Serviço temporariamente indisponível."}), 503
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT r.id_reserva, r.data_expiracao, rif.nome AS rifa_nome,
                      rif.valor_bilhete, b.numero
               FROM reserva r
               JOIN bilhete b ON b.reserva_id = r.id_reserva
               JOIN rifa rif ON rif.id_rifa = b.rifa_id
               WHERE r.usuario_id = %s AND r.status = 'ativa' AND r.data_expiracao > UTC_TIMESTAMP()""",
            (current_user,),
        )
        rows = cursor.fetchall()
        cursor.close()
    finally:
        conn.close()

    grouped = {}
    for row in rows:
        item = grouped.setdefault(
            row["id_reserva"],
            {
                "id_reserva": row["id_reserva"],
                "data_expiracao": row["data_expiracao"].isoformat(),
                "rifa_nome": row["rifa_nome"],
                "valor_bilhete": float(row["valor_bilhete"]),
                "numeros": [],
            },
        )
        item["numeros"].append(row["numero"])
    for item in grouped.values():
        item["numeros"].sort()
        item["valor_total"] = item["valor_bilhete"] * len(item["numeros"])
        del item["valor_bilhete"]
    return jsonify(list(grouped.values()))


@auth_bp.delete("/api/reservas/<int:reserva_id>/cancelar")
@token_required
def cancelar_reserva(current_user, reserva_id):
    conn = get_db()
    if conn is None:
        return jsonify({"erro": "Serviço temporariamente indisponível."}), 503
    try:
        conn.start_transaction()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE reserva SET status = 'expirada' WHERE id_reserva = %s AND usuario_id = %s AND status = 'ativa'",
            (reserva_id, current_user),
        )
        if cursor.rowcount != 1:
            conn.rollback()
            return jsonify({"erro": "Reserva ativa não encontrada."}), 404
        cursor.execute(
            "UPDATE bilhete SET status = 'disponivel', reserva_id = NULL WHERE reserva_id = %s AND status = 'reservado'",
            (reserva_id,),
        )
        conn.commit()
        cursor.close()
    except Exception:
        conn.rollback()
        return jsonify({"erro": "Não foi possível cancelar a reserva."}), 500
    finally:
        conn.close()
    return jsonify({"sucesso": True})


@auth_bp.get("/api/meus-bilhetes")
@token_required
def get_meus_bilhetes(current_user):
    # A consulta permanece disponível para histórico, sem habilitar nova venda.
    conn = get_db()
    if conn is None:
        return jsonify({"erro": "Serviço temporariamente indisponível."}), 503
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """SELECT b.id_bilhete, b.numero, b.data_compra, r.id_rifa,
                      r.nome AS rifa_nome, r.premio, r.data_sorteio,
                      r.valor_bilhete, s.numero_sorteado
               FROM bilhete b
               JOIN rifa r ON r.id_rifa = b.rifa_id
               LEFT JOIN sorteio s ON s.rifa_id = r.id_rifa
               WHERE b.usuario_id = %s AND b.status = 'pago'
               ORDER BY b.data_compra DESC""",
            (current_user,),
        )
        rows = cursor.fetchall()
        cursor.close()
    finally:
        conn.close()
    return jsonify(
        [
            {
                "id_bilhete": row["id_bilhete"],
                "numero": row["numero"],
                "rifa_nome": row["rifa_nome"],
                "rifa_id": row["id_rifa"],
                "premio": row["premio"],
                "data_compra": row["data_compra"].isoformat() if row["data_compra"] else None,
                "data_sorteio": row["data_sorteio"].isoformat() if row["data_sorteio"] else None,
                "valor": float(row["valor_bilhete"]),
                "numero_sorteado": row["numero_sorteado"],
                "premiado": row["numero_sorteado"] == row["numero"],
            }
            for row in rows
        ]
    )
