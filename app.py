from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from pymongo import MongoClient
from routes.auth_routes import auth_bp
from extensions import db, jwt, mail
from routes.product_routes import product_bp
from routes.cart_routes import cart_bp

app = Flask(__name__)  # Doğru bu şekilde olacak

# MySQL Bağlantı Ayarları
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/vtys_project'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# JWT ve Mail Ayarları
app.config['JWT_SECRET_KEY'] = 'supersecretkey'
app.config['JWT_IDENTITY_CLAIM'] = 'sub'

# Mail Ayarları (Outlook için)
app.config['MAIL_SERVER'] = 'smtp.office365.com'  #  DÜZGÜN SUNUCU ADI
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'zynpylmnzynpylmn@outlook.com'
app.config['MAIL_PASSWORD'] = 'vcfclypdjfoalinu'  # Bu bir uygulama şifresi olmalı

# Extensions başlat
db.init_app(app)
jwt.init_app(app)
mail.init_app(app)

''''# MongoDB Bağlantı Ayarları (extensionslardan sonra)
mongo_client = MongoClient('mongodb+srv://yalmanzeynep13:vtyssifre123@cluster0.drru65m.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
mongo_db = mongo_client['vtys_project']'''

# Blueprintler (routes)
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(product_bp, url_prefix='/api/product')
app.register_blueprint(cart_bp, url_prefix='/api/cart')

# Basit ana sayfa
@app.route('/')
def home():
    return "VTYS Projesi Çalışıyor!"

if __name__ == '__main__':  # dikkat: __name__ olmalı!
    app.run(debug=True)