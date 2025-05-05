from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail

from pymongo import MongoClient

# SQLAlchemy nesnesi
db = SQLAlchemy()

# JWT nesnesi
jwt = JWTManager()

# Mail nesnesi
mail = Mail()

# MongoDB bağlantısı
mongo_client = MongoClient('mongodb+srv://yalmanzeynep13:vtyssifre123@cluster0.drru65m.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')

# MongoDB veritabanı nesnesi
mongo_db = mongo_client['vtys_project']


