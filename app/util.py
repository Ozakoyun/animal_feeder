from datetime import datetime
from app import app, db, mqtt, scheduler
from app.models import Food, FoodDispensed, Timetable
#import RPi.GPIO as GPIO
#from RpiMotorLib import RpiMotorLib

gpio_pins = [6, 13, 19, 26]
#mymotor = RpiMotorLib.BYJMotor("MyMotorOne","28BYJ")


def setupGPIO():
    pass
    #GPIO.setmode(GPIO.BCM)
    #GPIO.setwarnings(False)


def add_jobs():
    times = Timetable.query.all()
    for time in times:
        scheduler.add_job(dispense_food, 'cron', (time.food_id, time.id, 1),
                          day_of_week=calculate_weekday(time.weekday),
                          hour=calculate_hour(time.output_time_minutes), id=str(time.id),
                          minute=calculate_minutes_remaining(time.output_time_minutes))


def get_food():
    food = Food.query.all()
    food = [(f.id, f.name) for f in food]
    return food


def dispense_food(food_id, timetable_id, trigger):
    food = Food.query.get(food_id)
    if food is not None and food.amount >= food.portion_size:
        #mymotor.motor_run(gpio_pins, 0.001, 42, True, False, "half", 0.001)
        trigger_word = None
        if trigger == 1:
            trigger_word = "automatic"
        else:
            trigger_word = "manual"
        mqtt.publish("animal_feeder", f"Food dispensed by {trigger_word} way !")
        dispension = FoodDispensed(amount_dispensed=food.portion_size, created=datetime.now(), trigger=trigger,
                                   food_id=food_id, timetable_id=timetable_id)
        db.session.add(dispension)
        food.amount = food.amount - food.portion_size
        db.session.commit()



def calculate_hour(minutes):
    return minutes//60

def calculate_minutes_remaining(minutes):
    return minutes-(calculate_hour(minutes)*60)


def calculate_weekday(weekday):
    if weekday == "Monday":
        return "mon"
    elif weekday == "Tuesday":
        return "tue"
    elif weekday == "Wednesday":
        return "wed"
    elif weekday == "Thursday":
        return "thu"
    elif weekday == "Friday":
        return "fri"
    elif weekday == "Saturday":
        return "sat"
    elif weekday == "Sunday":
        return "sun"
