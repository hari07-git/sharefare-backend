from flask import Blueprint, request, jsonify
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
auth = Blueprint('auth', __name__)
##
@auth.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email
            }
        }), 200
    else:
        return jsonify({'error': 'Invalid email or password'}), 401

@auth.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password required'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'User already exists'}), 409

    hashed_password = generate_password_hash(password)
    new_user = User(name=name, email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201
