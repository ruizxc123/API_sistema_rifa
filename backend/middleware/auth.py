from functools import wraps

import jwt
from flask import current_app, jsonify, request
from jwt import InvalidTokenError


def _read_token():
    header = request.headers.get("Authorization", "")
    scheme, separator, token = header.partition(" ")
    if not separator or scheme.lower() != "bearer" or not token.strip():
        return None
    return token.strip()


def _decode_token():
    token = _read_token()
    if not token:
        return None
    try:
        return jwt.decode(
            token,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"],
            options={"require": ["exp", "iat", "sub"]},
            issuer="api-sistema-rifa",
            audience="api-sistema-rifa-client",
        )
    except InvalidTokenError:
        return None


def token_required(view):
    @wraps(view)
    def decorated(*args, **kwargs):
        claims = _decode_token()
        if not claims:
            return jsonify({"erro": "Autenticação necessária ou token inválido."}), 401
        try:
            user_id = int(claims["sub"])
        except (KeyError, TypeError, ValueError):
            return jsonify({"erro": "Token inválido."}), 401
        return view(user_id, *args, **kwargs)

    return decorated


def admin_required(view):
    @wraps(view)
    def decorated(*args, **kwargs):
        claims = _decode_token()
        if not claims:
            return jsonify({"erro": "Autenticação necessária ou token inválido."}), 401
        try:
            user_id = int(claims["sub"])
        except (KeyError, TypeError, ValueError):
            return jsonify({"erro": "Token inválido."}), 401

        from utils.database import get_db

        conn = get_db()
        if conn is None:
            return jsonify({"erro": "Serviço temporariamente indisponível."}), 503
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT tipo, status FROM usuario WHERE id_usuario = %s",
                (user_id,),
            )
            user = cursor.fetchone()
            cursor.close()
        finally:
            conn.close()

        if not user or not user.get("status") or user.get("tipo") != "admin":
            return jsonify({"erro": "Acesso negado."}), 403
        return view(*args, **kwargs)

    return decorated
