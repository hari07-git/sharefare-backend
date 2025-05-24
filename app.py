from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from datetime import datetime, date
from models import db, Ride, User, Booking

# ----------------------
# App Initialization
# ----------------------
app = Flask(__name__)
CORS(app)

# ----------------------
# Configuration
# ----------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rides.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-change-me'

# ----------------------
# Initialize Extensions
# ----------------------
db.init_app(app)
jwt = JWTManager(app)

# ----------------------
# Root Route
# ----------------------
@app.route('/')
def index():
    return "🚗 ShareFare Backend is running!"

# ----------------------
# Search Rides
# ----------------------
@app.route('/api/search', methods=['GET'])
def search_rides():
    source = request.args.get('from')
    destination = request.args.get('to')
    date_str = request.args.get('date')

    if not source or not destination or not date_str:
        return jsonify({'error': 'Missing query parameters'}), 400

    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    rides = Ride.query.filter_by(source=source, destination=destination, date=date_obj).all()
    return jsonify([ride.to_dict() for ride in rides]), 200

# ----------------------
# Offer a Ride
# ----------------------
@app.route('/api/offer', methods=['POST'])
def offer_ride():
    data = request.get_json()
    required_fields = ['source', 'destination', 'date', 'price', 'driver']

    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Missing required field: {field}'}), 400

    try:
        ride_date = datetime.strptime(data['date'], "%Y-%m-%d").date()
        ride = Ride(
            source=data['source'],
            destination=data['destination'],
            date=ride_date,
            price=float(data['price']),
            driver=data['driver']
        )
        db.session.add(ride)
        db.session.commit()
        return jsonify({'message': 'Ride offered successfully!'}), 201

    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ----------------------
# Book a Ride
# ----------------------
@app.route('/api/book', methods=['POST'])
@jwt_required()
def book_ride():
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    ride_id = data.get('ride_id')

    if not ride_id:
        return jsonify({'error': 'Ride ID is required'}), 400

    ride = Ride.query.get(ride_id)

    if not ride:
        return jsonify({'error': 'Ride not found'}), 404

    existing_booking = Booking.query.filter_by(user_id=user.id, ride_id=ride_id).first()
    if existing_booking:
        return jsonify({'error': 'You have already booked this ride'}), 409

    booking = Booking(user_id=user.id, ride_id=ride.id)
    db.session.add(booking)
    db.session.commit()

    return jsonify({'message': 'Ride booked successfully', 'booking': booking.to_dict()}), 201

# ----------------------
# Get All Bookings for Logged-in User
# ----------------------
@app.route('/api/bookings', methods=['GET'])
@jwt_required()
def get_user_bookings():
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    bookings = Booking.query.filter_by(user_id=user.id).all()
    booking_data = [booking.to_dict() for booking in bookings]

    return jsonify({'bookings': booking_data}), 200

# ----------------------
# User Registration
# ----------------------
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    try:
        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully'}), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Email already registered'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
###
# ----------------------
# User Login
# ----------------------
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        token = create_access_token(identity=user.email)
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'email': user.email,
                'name': user.name
            }
        }), 200

    return jsonify({'error': 'Invalid email or password'}), 401

# ----------------------
# User Profile (GET & PUT)
# ----------------------
@app.route('/api/profile', methods=['GET', 'PUT'])
@jwt_required()
def profile():
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    if request.method == 'GET':
        return jsonify({
            'email': user.email,
            'name': user.name
        }), 200

    if request.method == 'PUT':
        data = request.get_json()
        new_name = data.get('name')
        if not new_name or not new_name.strip():
            return jsonify({'error': 'Name cannot be empty'}), 400

        user.name = new_name.strip()
        db.session.commit()
        return jsonify({'message': 'Profile updated', 'name': user.name}), 200

# ----------------------
# Run Server and Seed Database
# ----------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        if Ride.query.count() == 0:
            sample_rides = [
                Ride(source='Hyderabad', destination='Warangal', date=date(2025, 5, 5), price=250, driver='Akhil K.'),
                Ride(source='Chennai', destination='Bangalore', date=date(2025, 5, 6), price=500, driver='Sita R.'),
                Ride(source='Pune', destination='Mumbai', date=date(2025, 5, 7), price=300, driver='Rahul V.'),
                Ride(source='Delhi', destination='Jaipur', date=date(2025, 5, 8), price=450, driver='Neha M.')
            ]
            db.session.add_all(sample_rides)

        if User.query.count() == 0:
            sample_users = [
                User(name='Akhil', email='akhil@example.com', password=generate_password_hash('test123')),
                User(name='Sita', email='sita@example.com', password=generate_password_hash('test123')),
            ]
            db.session.add_all(sample_users)

        db.session.commit()

    app.run(debug=True)
