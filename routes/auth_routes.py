from flask import Blueprint, request, jsonify
from models.user_model import User
from extensions import db, mail
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_mail import Message
import bcrypt
import random
import string

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')

    if not email or not password or not role:
        return jsonify({'error': 'Tüm alanlar zorunludur!'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Bu email zaten kayıtlı!'}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    new_user = User(email=email, password=hashed_password.decode('utf-8'), role=role)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Kayıt başarılı!'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email ve şifre zorunludur!'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({'error': 'Geçersiz email veya şifre!'}), 401

    token_data = {
        'user_id': user.user_id,
        'role': user.role
    }
    access_token = create_access_token(identity=token_data)
    return jsonify({'access_token': access_token}), 200

@auth_bp.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Kullanıcı bulunamadı!'}), 404

    new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    user.password = hashed_password.decode('utf-8')
    db.session.commit()

    try:
        msg = Message(
            subject="Şifre Sıfırlama",  # Hata buradan geliyordu
            sender="zynpylmnzynpylmn@outlook.com",
            recipients=[user.email],
            body=f"Yeni şifreniz: {new_password}\nLütfen giriş yaptıktan sonra değiştirin."
        )
        mail.send(msg)
    except Exception as e:
        return jsonify({'error': f"E-posta gönderilemedi: {str(e)}"}), 500

    return jsonify({'message': 'Yeni şifre e-posta adresinize gönderildi!'}), 200

@auth_bp.route('/update_profile', methods=['POST'])
@jwt_required()
def update_profile():
    current = get_jwt_identity()
    user = User.query.filter_by(user_id=current['user_id']).first()

    if not user:
        return jsonify({'error': 'Kullanıcı bulunamadı!'}), 404

    data = request.get_json()
    new_email = data.get('email')
    new_password = data.get('password')

    if new_email:
        if User.query.filter_by(email=new_email).first():
            return jsonify({'error': 'Email zaten kullanımda!'}), 400
        user.email = new_email

    if new_password:
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        user.password = hashed_password.decode('utf-8')

    db.session.commit()
    return jsonify({'message': 'Profil güncellendi!'}), 200


