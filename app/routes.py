from app import app, db, scheduler
from flask import render_template, redirect, url_for, flash, Response
from app.forms import TimeTableForm, FoodForm, CancelForm, FoodDispenseForm
from app.models import Food, FoodDispensed, Timetable
from datetime import datetime, timedelta
from app.util import (
    get_food,
    dispense_food,
    calculate_weekday,
    calculate_hour,
    calculate_minutes_remaining,
    add_jobs,
    getOverview,
    getDetailedOverview,
    create_figure,
)
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import io

@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
def index():
    """
    Provides the index site of the application which allows food to be dispensed manually.
    :return: the HTML site enabling manual food dispension
    """
    form = FoodDispenseForm()
    if form.validate_on_submit():
        dispense_food(form.food.data, None, 0)
        return redirect(url_for("index"))
    return render_template("index.html", form=form, title="Home")


@app.route("/food")
def food():
    """
    Provides the food site of the application which allows food to be added, edited and deleted.
    :return: the HTML site enabling food to be added, edited and deleted
    """
    all_food = Food.query.all()
    return render_template("food.html", title="Food", all_food=all_food)


@app.route("/add_food", methods=["GET", "POST"])
def add_food():
    """
    Provides the add_food site of the application which allows food to be added.
    :return: the HTML site enabling food to be added
    """
    form = FoodForm()
    if form.cancel.data:
        return redirect(url_for("food"))
    if form.validate_on_submit():
        food = Food(
            name=form.name.data,
            portion_size=form.portion_size.data,
            amount=form.amount.data,
            created=datetime.utcnow(),
        )
        db.session.add(food)
        db.session.commit()
        return redirect(url_for("food"))
    return render_template("add_food.html", title="Add Food", form=form)


@app.route("/edit_food/<int:food_id>", methods=["GET", "POST"])
def edit_food(food_id):
    """
    Provides the edit_food site of the application which allows food to be edited.
    :param food_id: the id of the food to be edited
    :return: the HTML site enabling food to be edited
    """
    form = FoodForm()
    food = Food.query.filter_by(id=food_id).first()
    if form.cancel.data:
        return redirect(url_for("food"))
    if form.validate_on_submit():
        food.name = form.name.data
        food.portion_size = form.portion_size.data
        food.amount = form.amount.data
        food.created = datetime.utcnow()
        db.session.commit()
        return redirect(url_for("food"))
    form.name.data = food.name
    form.portion_size.data = food.portion_size
    form.amount.data = food.amount
    return render_template("edit_food.html", title="Edit Food", form=form)


@app.route("/delete_food/<int:food_id>", methods=["GET", "POST"])
def delete_food(food_id):
    """
    Provides the delete_food site of the application which allows food to be deleted.
    :param food_id: the id of the food to be deleted
    :return: the HTML site enabling food to be deleted
    """
    food = Food.query.filter_by(id=food_id).first()
    form = CancelForm()
    if form.cancel.data:
        return redirect(url_for("food"))
    if form.validate_on_submit():
        db.session.delete(food)
        db.session.commit()
        scheduler.remove_all_jobs()
        print(scheduler.get_jobs())
        add_jobs()
        print(scheduler.get_jobs())
        return redirect(url_for("food"))
    return render_template("delete_food.html", title="Delete Food", form=form)


@app.route("/timetable")
def timetable():
    """
    Provides the timetable site of the application which allows food to be dispensed automatically.
    :return: the HTML site enabling food to be dispensed automatically
    """
    all_timetable = Timetable.query.all()
    foods = []
    times = []
    for t in all_timetable:
        foods.append(Food.query.filter_by(id=t.food_id).first().name)
        delta = timedelta(minutes=t.output_time_minutes)
        start_of_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        result_datetime = start_of_day + delta
        result_time = result_datetime.time()
        times.append(result_time)
    return render_template(
        "timetable.html",
        title="Timetable",
        all_timetable=zip(all_timetable, foods, times),
        len_timetable=len(all_timetable),
    )


@app.route("/add_timetable", methods=["GET", "POST"])
def add_timetable():
    """
    Provides the add_timetable site of the application which allows food to be dispensed automatically.
    :return: the HTML site enabling food to be dispensed automatically
    """
    form = TimeTableForm()
    if form.validate_on_submit():
        timetable = Timetable(
            food_id=form.food.data,
            weekday=form.weekday.data,
            output_time_minutes=form.time.data.hour * 60 + form.time.data.minute,
        )
        db.session.add(timetable)
        db.session.commit()
        scheduler.add_job(
            dispense_food,
            "cron",
            (form.food.data, timetable.id, 1),
            day_of_week=calculate_weekday(form.weekday.data),
            hour=calculate_hour(form.time.data.hour * 60 + form.time.data.minute),
            id=str(timetable.id),
            minute=calculate_minutes_remaining(
                form.time.data.hour * 60 + form.time.data.minute
            ),
        )
        return redirect(url_for("timetable"))
    return render_template("add_timetable.html", title="Add Timetable", form=form)


@app.route("/edit_timetable/<int:timetable_id>", methods=["GET", "POST"])
def edit_timetable(timetable_id):
    """
    Provides the edit_timetable site of the application which allows food to be dispensed automatically.
    :param timetable_id: the id of the timetable to be edited
    :return: the HTML site enabling food to be dispensed automatically
    """
    form = TimeTableForm()
    timetable = Timetable.query.filter_by(id=timetable_id).first()
    print(timetable)
    if form.cancel.data:
        return redirect(url_for("timetable"))
    if form.validate_on_submit():
        timetable.food_id = form.food.data
        timetable.weekday = form.weekday.data
        timetable.output_time_minutes = form.time.data.hour * 60 + form.time.data.minute
        db.session.commit()
        scheduler.reschedule_job(
            str(timetable_id),
            trigger="cron",
            day_of_week=calculate_weekday(timetable.weekday),
            hour=calculate_hour(timetable.output_time_minutes),
            minute=calculate_minutes_remaining(timetable.output_time_minutes),
        )
        return redirect(url_for("timetable"))
    food_choices = get_food()
    food_choices.remove(
        (timetable.food_id, Food.query.filter_by(id=timetable.food_id).first().name)
    )
    form.food.choices = [
        (timetable.food_id, Food.query.filter_by(id=timetable.food_id).first().name)
    ] + food_choices
    form.food.data = timetable.food_id
    form.weekday.data = timetable.weekday
    return render_template("edit_timetable.html", title="Edit Timetable", form=form)


@app.route("/delete_timetable/<int:timetable_id>", methods=["GET", "POST"])
def delete_timetable(timetable_id):
    """
    Provides the delete_timetable site of the application which allows food to be dispensed automatically.
    :param timetable_id: the id of the timetable to be deleted
    :return: the HTML site enabling food to be dispensed automatically
    """
    timetable = Timetable.query.filter_by(id=timetable_id).first()
    form = CancelForm()
    if form.cancel.data:
        return redirect(url_for("timetable"))
    if form.validate_on_submit():
        db.session.delete(timetable)
        db.session.commit()
        scheduler.remove_all_jobs()
        print(scheduler.get_jobs())
        add_jobs()
        print(scheduler.get_jobs())
        return redirect(url_for("timetable"))
    return render_template("delete_timetable.html", title="Delete Timetable", form=form)

@app.route("/statistics")
def statistics():
    """
    Provides the statistics site of the application.
    :return: the HTML site to get an overview of the dispensed food
    """
    statistics = getOverview()
    return render_template("statistics.html", title="Statistics", statistics=statistics)

@app.route("/detailed_statistics/<int:food_id>")
def detailed_statistics(food_id):
    """
    Provides the detailed_statistics site of the application.
    :param food_id: the id of the food to get a detailed overview of
    :return: the HTML site to get a detailed overview of the dispensed food
    """
    foodName, dispenses = getDetailedOverview(food_id)
    return render_template("detailed_statistics.html", title="Detailed Statistics", foodName=foodName, dispenses=dispenses, food_id=food_id)

@app.route("/plot.png/<int:food_id>")
def plot_png(food_id):
    """
    Provides the plot_png site of the application.
    :param food_id: the id of the food to get a plot of
    :return: image of plot
    """
    fig = create_figure(food_id)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype="image/png")

@app.template_filter("datetimeformat")
def datetimeformat(value, datetime_format="%d.%m.%Y at %H:%M:%S"):
    """
    Converts a datetime object into a string with the given format.
    :param value: the datetime object to be converted
    :param datetime_format: the format of the datetime object
    :return: the datetime object as a string with the given format
    """
    return value.strftime(datetime_format)


@app.template_global(name="zip")
def _zip(*args, **kwargs):  # to not overwrite builtin zip in globals
    """
    Returns the zip function.
    :param args: the arguments of the zip function
    :param kwargs: the keyword arguments of the zip function
    :return: the zip function
    """
    return __builtins__.zip(*args, **kwargs)


@app.route("/test")
def test():
    # Delete entries from all tables
    counter = 0
    food_dispensed = FoodDispensed.query.all()
    for f in food_dispensed:
        db.session.delete(f)
        counter += 1
    print(f"Deleted {counter} entries from FoodDispensed table")

    # Will be deleted because cascade is set to all
    # counter = 0
    # timetable = Timetable.query.all()
    # for t in timetable:
    #    db.session.delete(t)
    #    counter += 1
    # print(f"Deleted {counter} entries from Timetable table")

    counter = 0
    food = Food.query.all()
    for f in food:
        db.session.delete(f)
        counter += 1
    print(f"Deleted {counter} entries from Food table")

    db.session.commit()
    print("All tables cleared")

    # Add entries to Food table
    f1 = Food(name="Purina One", portion_size=10, amount=100, created=datetime.utcnow())
    f2 = Food(
        name="Royal Canin", portion_size=10, amount=100, created=datetime.utcnow()
    )
    f3 = Food(name="Hills", portion_size=10, amount=100, created=datetime.utcnow())
    f4 = Food(name="Iams", portion_size=10, amount=100, created=datetime.utcnow())

    db.session.add(f1)
    db.session.add(f2)
    db.session.add(f3)
    db.session.add(f4)
    db.session.commit()
    print("Added entries to Food table")

    dt = datetime.fromisoformat("2023-05-20 00:00:00")
    f1 = FoodDispensed(
        amount_dispensed=10, created=dt, trigger=0, food_id=1
    )
    dt = datetime.fromisoformat("2023-05-21 00:00:00")
    f2 = FoodDispensed(
        amount_dispensed=3, created=dt, trigger=0, food_id=1
    )
    dt = datetime.fromisoformat("2023-05-22 00:00:00")
    f3 = FoodDispensed(
        amount_dispensed=8, created=dt, trigger=0, food_id=1
    )
    dt = datetime.fromisoformat("2023-05-23 00:00:00")
    f4 = FoodDispensed(
        amount_dispensed=15, created=dt, trigger=0, food_id=1
    )

    f5 = FoodDispensed(
        amount_dispensed=1, created=datetime.utcnow(), trigger=0, food_id=2
    )
    f6 = FoodDispensed(
        amount_dispensed=1, created=datetime.utcnow(), trigger=0, food_id=2
    )
    f7 = FoodDispensed(
        amount_dispensed=1, created=datetime.utcnow(), trigger=0, food_id=2
    )
    f8 = FoodDispensed(
        amount_dispensed=1, created=datetime.utcnow(), trigger=0, food_id=2
    )

    f9 = FoodDispensed(
        amount_dispensed=2, created=datetime.utcnow(), trigger=0, food_id=3
    )
    f10 = FoodDispensed(
        amount_dispensed=2, created=datetime.utcnow(), trigger=0, food_id=3
    )
    f11 = FoodDispensed(
        amount_dispensed=2, created=datetime.utcnow(), trigger=0, food_id=3
    )
    f12 = FoodDispensed(
        amount_dispensed=2, created=datetime.utcnow(), trigger=0, food_id=3
    )

    db.session.add(f1)
    db.session.add(f2)
    db.session.add(f3)
    db.session.add(f4)
    db.session.add(f5)
    db.session.add(f6)
    db.session.add(f7)
    db.session.add(f8)
    db.session.add(f9)
    db.session.add(f10)
    db.session.add(f11)
    db.session.add(f12)
    db.session.commit()

    # Add entries to Timetable table
    t1 = Timetable(output_time_minutes=650, weekday="Monday", food_id=1)
    t2 = Timetable(output_time_minutes=650, weekday="Wednesday", food_id=2)
    t3 = Timetable(output_time_minutes=650, weekday="Friday", food_id=3)
    t4 = Timetable(output_time_minutes=650, weekday="Sunday", food_id=4)

    db.session.add(t1)
    db.session.add(t2)
    db.session.add(t3)
    db.session.add(t4)
    db.session.commit()
    print("Added entries to Timetable table")
    return redirect(url_for("index"))
