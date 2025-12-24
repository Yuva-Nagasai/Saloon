import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-salon-chic'
    # Using a local MySQL database. User needs to ensure this DB exists.
    # URI format: mysql+pymysql://username:password@host/dbname
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:password@localhost/salon_chic_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
