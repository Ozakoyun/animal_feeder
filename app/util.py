from app import app, db
from app.models import Food, FoodDispensed, Timetable

def get_food():
    food = Food.query.all()
    food = [(f.id, f.name) for f in food]
    return food