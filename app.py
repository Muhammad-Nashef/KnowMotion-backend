# import necessary libraries
from flask import Flask, jsonify, request
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import jwt
from datetime import datetime, timedelta
import cloudinary_config
import cloudinary
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt
from config import Config
from routes.auth import auth_bp, bcrypt
from routes.subCategories import sub_bp
from routes.mainCategories import main_bp
from routes.answers import answers_bp
from routes.Questions import questions_bp
import psycopg2

# initialize Flask app and configurations
#load_dotenv()
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = Config.SECRET_KEY
jwt = JWTManager(app)

bcrypt.init_app(app)
CORS(app, resources={r"/*": {"origins": "*"}})
#SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

"""CORS(app, resources={r"/*": {"origins": "*"}})
bcrypt = Bcrypt(app)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")"""

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/api")
app.register_blueprint(sub_bp)
app.register_blueprint(main_bp)
app.register_blueprint(answers_bp)
app.register_blueprint(questions_bp)

from flask_jwt_extended import exceptions

@jwt.invalid_token_loader
def invalid_token_callback(error):
    print("Invalid token:", error)
    return jsonify({"msg": "Invalid token"}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    print("Missing token:", error)
    return jsonify({"msg": "Missing token"}), 401

@app.route('/')
def home():
    return "KnowMotion backend is running!"

if __name__ == "__main__":
    app.run(debug=True)
