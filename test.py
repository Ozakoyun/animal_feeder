from app import db
from app.models import Food, FoodDispensed, Timetable
from datetime import datetime

# Delete entries from all tables
counter = 0
food = Food.query.all()
for f in food:
    db.session.delete(f)
    counter += 1
print(f'Deleted {counter} entries from Food table')

counter = 0
food_dispensed = FoodDispensed.query.all()
for f in food_dispensed:
    db.session.delete(f)
    counter += 1
print(f'Deleted {counter} entries from FoodDispensed table')

counter = 0
timetable = Timetable.query.all()
for t in timetable:
    db.session.delete(t)
    counter += 1
print(f'Deleted {counter} entries from Timetable table')

db.session.commit()
print('All tables cleared')

# Add entries to Food table
f1 = Food(name='Purina One', portion_size=10, amount=100, created=datetime.utcnow())
f2 = Food(name='Royal Canin', portion_size=10, amount=100, created=datetime.utcnow())
f3 = Food(name='Hills', portion_size=10, amount=100, created=datetime.utcnow())
f4 = Food(name='Iams', portion_size=10, amount=100, created=datetime.utcnow())

db.session.add(f1)
db.session.add(f2)
db.session.add(f3)
db.session.add(f4)
db.session.commit()
print('Added entries to Food table')