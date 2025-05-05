from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import mongo_db, mail
from models.user_model import User
from flask_mail import Message

cart_bp = Blueprint('cart_bp', __name__)

@cart_bp.route('/add_to_cart', methods=['POST'])
@jwt_required()
def add_to_cart():
    current = get_jwt_identity()
    user_id = current['user_id']
    role = current['role']

    if role != 'customer':
        return jsonify({'error': 'Sadece müşteriler sepet işlemi yapabilir!'}), 403

    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    cart = mongo_db.carts.find_one({'user_id': user_id})
    if not cart:
        cart_data = {
            'user_id': user_id,
            'products': [{'product_id': product_id, 'quantity': quantity}]
        }
        mongo_db.carts.insert_one(cart_data)
    else:
        found = False
        for item in cart['products']:
            if item['product_id'] == product_id:
                item['quantity'] += quantity
                found = True
                break
        if not found:
            cart['products'].append({'product_id': product_id, 'quantity': quantity})
        mongo_db.carts.update_one({'user_id': user_id}, {'$set': {'products': cart['products']}})
    return jsonify({'message': 'Ürün sepete eklendi!'}), 200

@cart_bp.route('/view_cart', methods=['GET'])
@jwt_required()
def view_cart():
    current = get_jwt_identity()
    user_id = current['user_id']
    role = current['role']

    if role != 'customer':
        return jsonify({'error': 'Sadece müşteriler görebilir!'}), 403

    cart = mongo_db.carts.find_one({'user_id': user_id})
    if not cart:
        return jsonify({'message': 'Sepet boş!'}), 200
    return jsonify(cart['products']), 200

@cart_bp.route('/remove_from_cart', methods=['POST'])
@jwt_required()
def remove_from_cart():
    current = get_jwt_identity()
    user_id = current['user_id']
    role = current['role']

    data = request.get_json()
    product_id = data.get('product_id')

    cart = mongo_db.carts.find_one({'user_id': user_id})
    if not cart:
        return jsonify({'error': 'Sepet bulunamadı!'}), 404

    updated = [item for item in cart['products'] if item['product_id'] != product_id]
    mongo_db.carts.update_one({'user_id': user_id}, {'$set': {'products': updated}})

    return jsonify({'message': 'Ürün sepetten silindi!'}), 200

@cart_bp.route('/checkout', methods=['POST'])
@jwt_required()
def checkout():
    current = get_jwt_identity()
    user_id = current['user_id']
    role = current['role']

    if role != 'customer':
        return jsonify({'error': 'Sadece müşteriler sepet işlemi yapabilir!'}), 403

    cart = mongo_db.carts.find_one({'user_id': user_id})
    if not cart or not cart.get('products'):
        return jsonify({'error': 'Sepet boş!'}), 400

    new_order = {
        'user_id': user_id,
        'products': cart['products'],
        'status': 'Sipariş Alındı'
    }
    mongo_db.orders.insert_one(new_order)
    mongo_db.carts.update_one({'user_id': user_id}, {'$set': {'products': []}})

    user = User.query.filter_by(user_id=user_id).first()
    try:
        if user:
            msg = Message(
                subject="Sipariş Onayı",
                sender="zynpylmnzynpylmn@outlook.com",
                recipients=[user.email],
                body="Siparişiniz başarıyla alınmıştır!"
            )
            mail.send(msg)
    except Exception as e:
        return jsonify({'warning': f'Sipariş başarılı ancak e-posta gönderilemedi: {str(e)}'}), 201

    return jsonify({'message': 'Sipariş oluşturuldu!'}), 201