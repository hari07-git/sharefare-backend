from app import db
from models import Ride

ride1 = Ride(from_location="Hyderabad", to_location="Warangal", date="2025-05-05", price="250", driver_name="Akhil K.")
ride2 = Ride(from_location="Chennai", to_location="Bangalore", date="2025-05-06", price="500", driver_name="Sita R.")

db.session.add_all([ride1, ride2])
db.session.commit()
