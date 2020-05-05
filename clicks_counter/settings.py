import os

HOST = os.environ.get("HOST")
PORT = int(os.environ.get("PORT"))
REDIS_URI = os.environ.get("REDIS_URI")
DB_UPDATE_SEC = float(os.environ.get("DB_UPDATE_SEC"))

DB_HOST = os.environ.get("DB_HOST")
DB_PORT = int(os.environ.get("DB_PORT"))
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB = os.environ.get("DB")
