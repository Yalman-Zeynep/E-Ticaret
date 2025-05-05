from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import mongo_db
import uuid

product_bp = Blueprint('product_bp', __name__)

@product_bp.route('/add_product', methods=['POST'])
@jwt_required()
def add_product():
    current = get_jwt_identity()
    if current['role'] != 'supplier':
        return jsonify({'error': 'Sadece tedarikçiler ürün ekleyebilir!'}), 403

    data = request.get_json()
    name = data.get('name')
    price = data.get('price')
    stock = data.get('stock')
    print(data)
    if not name or not price or not stock:
        return jsonify({'error': 'Tüm alanlar zorunludur!'}), 400

    new_product = {
        "product_id": str(uuid.uuid4()),
        "name": name,
        "price": price,
        "stock": stock,
        "supplier_id": current['user_id']
    }
    print(new_product )
    mongo_db.products.insert_one(new_product)
    return jsonify({'message': 'Ürün eklendi!'}), 201

@product_bp.route('/list_products', methods=['GET'])
def list_products():
    products = mongo_db.products.find()
    result = []
    for p in products:
        result.append({
            "product_id": p.get("product_id"),
            "name": p.get("name"),
            "price": p.get("price"),
            "stock": p.get("stock")
        })
    return jsonify(result), 200


