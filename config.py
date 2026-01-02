import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    DB_HOST = os.getenv("DB_HOST")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME = os.getenv("DB_NAME")
    CLOUDINARY_CLOUD_NAME = os.getenv("CLOUD_NAME")
    CLOUDINARY_API_KEY = os.getenv("CLOUD_API_KEY")
    CLOUDINARY_API_SECRET = os.getenv("CLOUD_API_SECRET")