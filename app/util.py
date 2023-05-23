from app import app, db#, mqtt
from app.models import Food, FoodDispensed, Timetable
from sqlalchemy import func
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

#import RPi.GPIO as GPIO
#from RpiMotorLib import RpiMotorLib


#gpio_pins = [6,13,19,26]
#mymotor = RpiMotorLib.BYJMotor("MyMotorOne","28BYJ")


#def setupGPIO():
#    GPIO.setmode(GPIO.BCM)
#    GPIO.setwarnings(False)


def get_food():
    food = Food.query.all()
    food = [(f.id, f.name) for f in food]
    return food


#def dispense_food(trigger="automatic"):
#    mymotor.motor_run(gpio_pins, 0.001, 42, True, False, "half", 0.001)
#    mqtt.publish("animal_feeder",f"Food dispensed by {trigger} way !")


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

def getOverview():
    food = Food.query.all()
    statistics = []
    for f in food:
        entry = {}
        entry["id"] = f.id
        entry["name"] = f.name
        lastDispensed = FoodDispensed.query.filter_by(food_id=f.id).order_by(FoodDispensed.created.desc()).first()
        if lastDispensed is not None:
            entry["lastDispensed"] = lastDispensed.created.strftime("%d.%m.%Y at %H:%M:%S")
        else:
            entry["lastDispensed"] = "Never dispensed"
        entry["totalDispenses"] = FoodDispensed.query.filter_by(food_id=f.id).count()
        amountDispensed = FoodDispensed.query.with_entities(func.sum(FoodDispensed.amount_dispensed)).filter_by(food_id=f.id).scalar()
        if amountDispensed is not None:
            entry["amountDispensed"] = amountDispensed
        else:
            entry["amountDispensed"] = 0
        entry["amountRemaining"] = f.amount - entry["amountDispensed"]
        statistics.append(entry)
    return statistics

def getDetailedOverview(foodId):
    foodName = Food.query.filter_by(id=foodId).first().name
    dispenses = FoodDispensed.query.filter_by(food_id=foodId).order_by(FoodDispensed.created.desc()).all()
    for d in dispenses:
        if d.trigger == 0:
            d.trigger = "manual"
        elif d.trigger == 1:
            d.trigger = "automatic"
        else:
            d.trigger = "unknown"
    return foodName, dispenses


def create_figure(food_id):
    food_dispensed_list = db.session.query(FoodDispensed).filter_by(food_id=food_id).all()

    x_values = [fd.created for fd in food_dispensed_list]
    x_values = [x.strftime("%d.%m.%Y") for x in x_values]
    y_values = [fd.amount_dispensed for fd in food_dispensed_list]

    print(x_values)
    print(y_values)

    fig = Figure()
    ax = fig.add_subplot(111)
    ax.plot(x_values, y_values)
    ax.set_xlabel('Created')
    ax.set_ylabel('Amount Dispensed')
    ax.set_title('Food Dispensed over Time')
    ax.set_xticklabels(x_values, rotation=45)
    #canvas.print_figure('app/static/plot.png')
    fig.subplots_adjust(bottom=0.3)
    return fig