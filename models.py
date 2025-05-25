from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

# ----------------------
# Ride Model
# ----------------------
class Ride(db.Model):
    __tablename__ = 'rides'

    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Float, nullable=False)
    driver = db.Column(db.String(100), nullable=False)

    # Relationship to bookings
    bookings = db.relationship('Booking', backref='ride', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'source': self.source,
            'destination': self.destination,
            'date': self.date.strftime('%Y-%m-%d'),
            'price': self.price,
            'driver': self.driver
        }

    def __repr__(self):
        return f'<Ride {self.source} to {self.destination} on {self.date}>'

# ----------------------
# User Model
# ----------------------
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(200), nullable=False)

    # Relationship to bookings
    bookings = db.relationship('Booking', backref='user', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email
        }

    def __repr__(self):
        return f'<User {self.email}>'

# ----------------------
# Booking Model
# ----------------------
class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ride_id = db.Column(db.Integer, db.ForeignKey('rides.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='booked')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ride_id': self.ride_id,
            'status': self.status,
            'user': self.user.name if self.user else None,
            'ride': {
                'source': self.ride.source,
                'destination': self.ride.destination,
                'date': self.ride.date.strftime('%Y-%m-%d'),
                'driver': self.ride.driver,
                'price': self.ride.price
            } if self.ride else None
        }

    def __repr__(self):
        return f'<Booking User {self.user_id} Ride {self.ride_id}>'
