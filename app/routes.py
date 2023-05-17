from app import app, db, scheduler
from flask import render_template, redirect, url_for
from app.forms import TimeTableForm, FoodForm, CancelForm
from app.models import Food, FoodDispensed, Timetable
from datetime import datetime, timedelta
from app.util import get_food, dispense_food, calculate_weekday, calculate_hour, calculate_minutes_remaining


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", title="Home")

@app.route("/dispensing/", methods=["POST"])
def dispense():
    dispense_food("manual")
    return render_template("index.html", title="Home")


@app.route("/food")
def food():
    all_food = Food.query.all()
    return render_template("food.html", title="Food", all_food=all_food)


@app.route("/add_food", methods=["GET", "POST"])
def add_food():
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
    food = Food.query.filter_by(id=food_id).first()
    form = CancelForm()
    if form.cancel.data:
        return redirect(url_for("food"))
    if form.validate_on_submit():
        db.session.delete(food)
        db.session.commit()
        return redirect(url_for("food"))
    return render_template("delete_food.html", title="Delete Food", form=form)


@app.route("/timetable")
def timetable():
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
    form = TimeTableForm()
    if form.validate_on_submit():
        timetable = Timetable(
            food_id=form.food.data,
            weekday=form.weekday.data,
            output_time_minutes=form.time.data.hour * 60 + form.time.data.minute,
        )
        db.session.add(timetable)
        db.session.commit()
        scheduler.add_job(dispense_food, 'cron', day_of_week=calculate_weekday(form.weekday.data),
                          hour=calculate_hour(form.time.data.hour * 60 + form.time.data.minute), id=str(timetable.id),
                          minute=calculate_minutes_remaining(form.time.data.hour * 60 + form.time.data.minute))
        return redirect(url_for("timetable"))
    return render_template("add_timetable.html", title="Add Timetable", form=form)


@app.route("/edit_timetable/<int:timetable_id>", methods=["GET", "POST"])
def edit_timetable(timetable_id):
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
        scheduler.reschedule_job(str(timetable.food_id), trigger='cron',
                                 day_of_week=calculate_weekday(timetable.weekday),
                                 hour=calculate_hour(timetable.output_time_minutes),
                                 minute=calculate_minutes_remaining(timetable.output_time_minutes))
        return redirect(url_for("timetable"))
    food_choices = get_food()
    food_choices.remove((timetable.food_id, Food.query.filter_by(id=timetable.food_id).first().name))
    form.food.choices = [(timetable.food_id, Food.query.filter_by(id=timetable.food_id).first().name)] + food_choices
    form.food.data = timetable.food_id
    form.weekday.data = timetable.weekday
    return render_template("edit_timetable.html", title="Edit Timetable", form=form)

@app.route("/delete_timetable/<int:timetable_id>", methods=["GET", "POST"])
def delete_timetable(timetable_id):
    timetable = Timetable.query.filter_by(id=timetable_id).first()
    form = CancelForm()
    if form.cancel.data:
        return redirect(url_for("timetable"))
    if form.validate_on_submit():
        db.session.delete(timetable)
        db.session.commit()
        scheduler.remove_job(str(timetable_id))
        return redirect(url_for("timetable"))
    return render_template("delete_timetable.html", title="Delete Timetable", form=form)

@app.template_filter("datetimeformat")
def datetimeformat(value, datetime_format="%d.%m.%Y at %H:%M:%S"):
    return value.strftime(datetime_format)


@app.template_global(name="zip")
def _zip(*args, **kwargs):  # to not overwrite builtin zip in globals
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
    return render_template("index.html", title="Home")
