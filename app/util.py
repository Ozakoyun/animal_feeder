from datetime import datetime

from flask import flash
from sqlalchemy import func

from app import app, db, mqtt, scheduler
from app.models import Food, FoodDispensed, Timetable
import RPi.GPIO as GPIO
from RpiMotorLib import RpiMotorLib
from matplotlib.figure import Figure

gpio_pins = [6, 13, 19, 26]
mymotor = RpiMotorLib.BYJMotor("MyMotorOne","28BYJ")


def setupGPIO():
    """
    This function sets up the GPIO mode and adjusts if warnings should be displayed.
    It is used automatically by the library RPi.GPIO when the application launches.
    """
    pass
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)


def add_jobs():
    """
    This function enables all timetables to be converted into "jobs", which then get executed at the set time
    saved in the database. All TimeTable objects are queried and subsequently turned into jobs. The day of the week,
    hour and minute have to be calculated back into the correct measurement by calling the respective functions. The id
    of a job is the id of the associated TimeTable object. 'cron' sets the job execution to weekly.
    """
    times = Timetable.query.all()
    for time in times:
        scheduler.add_job(dispense_food, 'cron', (time.food_id, time.id, 1),
                          day_of_week=calculate_weekday(time.weekday),
                          hour=calculate_hour(time.output_time_minutes), id=str(time.id),
                          minute=calculate_minutes_remaining(time.output_time_minutes))


def get_food():
    """
    This function queries all Food objects and returns them as a list of tuples containing the id and name of the food.
    """
    food = Food.query.all()
    food = [(f.id, f.name) for f in food]
    return food


def dispense_food(food_id, timetable_id, trigger):
    """
    Dispense food, send the MQTT message and save the dispension in the database.
    :param food_id: the id of the food being dispensed
    :param timetable_id: the id of the triggering TimeTable object or None
    :param trigger: 1 if automatic triggering of dispension; 0 if manual triggering of dispension
    """
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
        if trigger != 1:
            flash("Food successfully dispensed!")
    elif trigger != 1:
        flash("Food could not be dispensed! Ensure that enough food is registered in the application!")




def calculate_hour(minutes):
    """
    Calculates given minutes to hours by using floor division.
    :param minutes: the minutes to be converted into hours
    :return: amount of full hours in given minutes
    """
    return minutes//60

def calculate_minutes_remaining(minutes):
    """
    Calculates given minutes to minutes left after all full hours are subtracted by floor division.
    :param minutes: the minutes to be converted into remaining minutes by subtracting all full hours
    :return: remaining minutes after subtracting all full hours
    """
    return minutes-(calculate_hour(minutes)*60)


def calculate_weekday(weekday):
    """
    Converts the full name of a weekday to its three lettered short description for usage in the job scheduling.
    :param weekday: the weekday in full writing, e.x. Monday
    :returns: the given weekday in short description, e.x. mon
    """
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
    """
    This function queries all Food objects and returns them as a list of dictionaries containing the id, name, lastDispensed, totalDispenses, amountDispensed and amountRemaining of the food.
    :returns: a list of dictionaries containing the id, name, lastDispensed, totalDispenses, amountDispensed and amountRemaining for each food object
    """
    food = Food.query.all()
    statistics = []
    for f in food:
        entry = {}
        entry["id"] = f.id
        entry["name"] = f.name
        lastDispensed = (
            FoodDispensed.query.filter_by(food_id=f.id)
            .order_by(FoodDispensed.created.desc())
            .first()
        )
        if lastDispensed is not None:
            entry["lastDispensed"] = lastDispensed.created.strftime(
                "%d.%m.%Y at %H:%M:%S"
            )
        else:
            entry["lastDispensed"] = "Never dispensed"
        entry["totalDispenses"] = FoodDispensed.query.filter_by(food_id=f.id).count()
        amountDispensed = (
            FoodDispensed.query.with_entities(func.sum(FoodDispensed.amount_dispensed))
            .filter_by(food_id=f.id)
            .scalar()
        )
        if amountDispensed is not None:
            entry["amountDispensed"] = amountDispensed
        else:
            entry["amountDispensed"] = 0
        entry["amountRemaining"] = f.amount
        statistics.append(entry)
    return statistics


def getDetailedOverview(foodId):
    """
    This function queries all FoodDispensed objects for a given foodId and returns them as a list of tuples containing the name of the food and the dispenses.
    :param: foodId: the id of the food for which the dispenses should be queried
    :returns: a tuple containing the name of the food and a list of tuples containing the amount dispensed, the date and time of the dispense and the trigger of the dispense
    """
    foodName = Food.query.filter_by(id=foodId).first().name
    dispenses = (
        FoodDispensed.query.filter_by(food_id=foodId)
        .order_by(FoodDispensed.created.desc())
        .all()
    )
    for d in dispenses:
        if d.trigger == 0:
            d.trigger = "manual"
        elif d.trigger == 1:
            d.trigger = "automatic"
        else:
            d.trigger = "unknown"
    return foodName, dispenses


def create_figure(food_id):
    """
    This function queries all FoodDispensed objects for a given foodId and returns them as a matplotlib figure.
    :param: foodId: the id of the food for which the dispenses should be queried
    :returns: a matplotlib figure containing the amount dispensed over time
    """
    food_dispensed_list = (
        db.session.query(FoodDispensed).filter_by(food_id=food_id).all()
    )

    x_values = [fd.created.strftime("%d.%m.%Y") for fd in food_dispensed_list]
    y_values = [fd.amount_dispensed for fd in food_dispensed_list]

    data_dict = {}
    for x, y in zip(x_values, y_values):
        if x in data_dict:
            data_dict[x] += y
        else:
            data_dict[x] = y

    x_values = list(data_dict.keys())
    y_values = list(data_dict.values())

    fig = Figure()
    ax = fig.add_subplot(111)
    ax.plot(x_values, y_values)
    ax.set_xlabel("Created")
    ax.set_ylabel("Amount Dispensed")
    ax.set_title("Food Dispensed over Time")
    ax.set_xticklabels(x_values, rotation=45)
    fig.subplots_adjust(bottom=0.3)
    return fig