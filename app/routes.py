from app import app, db
from flask import render_template
from app.forms import TimeTableForm

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

@app.route('/add_timetable')
def add_timetable():
    form = TimeTableForm()
    return render_template('add_timetable.html', title='Add Timetable', form=form)