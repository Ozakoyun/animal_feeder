from app import app, db, mqtt
from app.models import Food, FoodDispensed, Timetable
import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib


gpio_pins = [6,13,19,26]
mymotor = RpiMotorLib.BYJMotor("MyMotorOne","28BYJ")


def setupGPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)


def get_food():
    food = Food.query.all()
    food = [(f.id, f.name) for f in food]
    return food


def dispense_food(trigger="automatic"):
    mymotor.motor_run(gpio_pins, 0.001, 42, True, False, "half", 0.001)
    mqtt.publish("animal_feeder",f"Food dispensed by {trigger} way !")


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
