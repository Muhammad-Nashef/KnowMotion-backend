from flask import Blueprint, request, jsonify
from models.db import get_db_connection
from flask_bcrypt import Bcrypt
#from flask_jwt_extended import create_access_token
from config import Config
from datetime import datetime, timedelta
import jwt
from psycopg2.extras import RealDictCursor

auth_bp = Blueprint("auth", __name__)
bcrypt = Bcrypt()

@auth_bp.route("/login", methods=["POST"])
# route for user login
def login():

    data = request.json
    username = data.get("username")
    password = data.get("password")
    print(f"Login attempt for user: {username}")
    print(f"Password provided: {password}")
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    conn.close()
    print(f"User fetched from DB: {user['password_hash']}")
    if not user or not bcrypt.check_password_hash(user['password_hash'], password):
        return jsonify({"message": "Invalid credentials"}), 401

    token = jwt.encode({
    "id": user['id'],
    "username": user['username'],
    "role": user['role'],
    "exp": datetime.utcnow() + timedelta(hours=2)
}, Config.SECRET_KEY, algorithm="HS256")
    return jsonify({"token": token, "role": user['role']})