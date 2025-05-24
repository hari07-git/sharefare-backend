from flask import Blueprint, request, jsonify
from models import db, Ride

api = Blueprint('api', __name__)

# #----------------------
# Offer Ride
# ----------------------
@api.route('/api/offer', methods=['POST'])
def offer_ride():
    try:
        data = request.get_json()
        required_fields = ['source', 'destination', 'date', 'price', 'driver']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        ride = Ride(
            source=data['source'],
            destination=data['destination'],
            date=data['date'],
            price=float(data['price']),
            driver=data['driver']
        )
        db.session.add(ride)
        db.session.commit()

        return jsonify({'message': 'Ride offered successfully!'}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ----------------------
# Search Rides
# ----------------------
@api.route('/api/search', methods=['GET'])
def search_rides():
    source = request.args.get('from')
    destination = request.args.get('to')
    date = request.args.get('date')

    if not source or not destination or not date:
        return jsonify({'error': 'Missing query parameters'}), 400

    results = Ride.query.filter_by(source=source, destination=destination, date=date).all()
    return jsonify([r.to_dict() for r in results]), 200
