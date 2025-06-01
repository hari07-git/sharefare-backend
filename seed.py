from app import app
from models import db, Ride, User
from datetime import date

with app.app_context():
    # Clear existing data
    Ride.query.delete()
    User.query.delete()

    # Create users
    user1 = User(name="Alice", email="alice@example.com", password="alice123")
    user2 = User(name="Bob", email="bob@example.com", password="bob123")

    # Add users to DB
    db.session.add_all([user1, user2])
    db.session.commit()

    # Create rides
    ride1 = Ride(
        source="Hyderabad",
        destination="Bangalore",
        date=date(2025, 5, 25),
        price=500.0,
        driver="Alice"
    )
    ride2 = Ride(
        source="Chennai",
        destination="Hyderabad",
        date=date(2025, 5, 25),
        price=450.0,
        driver="Bob"
    )

    db.session.add_all([ride1, ride2])
    db.session.commit()

    print("Database seeded successfully!")
