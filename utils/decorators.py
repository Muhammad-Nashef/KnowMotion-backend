from functools import wraps
#from flask_jwt_extended import jwt_required, get_jwt
from flask import jsonify
import jwt
from flask import jsonify, request
from config import Config


def admin_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing token"}), 401
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        if payload.get("role") != "admin":
            return jsonify({"error": "Unauthorized"}), 403

        return fn(*args, **kwargs)
    return wrapper