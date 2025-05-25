from flask import Blueprint, request, jsonify
from models import db, Ride, Booking, User
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

api = Blueprint('api', __name__)

# ----------------------
# Search Rides
# ----------------------
@api.route('/search', methods=['GET'])
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

    results = Ride.query.filter_by(source=source, destination=destination, date=date_obj).all()
    return jsonify([r.to_dict() for r in results]), 200

# ----------------------
# Offer Ride
# ----------------------
@api.route('/offer', methods=['POST'])
def offer_ride():
    try:
        data = request.get_json()
        required_fields = ['source', 'destination', 'date', 'price', 'driver']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400

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
@api.route('/book', methods=['POST'])
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
# Get User Bookings
# ----------------------
@api.route('/bookings', methods=['GET'])
@jwt_required()
def get_user_bookings():
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()

    if not user:
        return jsonify({'error': 'User not found'}), 404

    bookings = Booking.query.filter_by(user_id=user.id).all()
    return jsonify({'bookings': [b.to_dict() for b in bookings]}), 200
