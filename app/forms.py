from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    SelectField,
    IntegerField,
    TimeField,
)
from wtforms.validators import DataRequired
from datetime import datetime
from app.util import get_food


class ManualFoodForm(FlaskForm):
    submit = SubmitField("Feed")


class TimeTableForm(FlaskForm):
    food = SelectField(
        label="Select food",
        validators=[DataRequired()],
        choices=get_food(),
    )
    weekday = SelectField(
        choices=[
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ],
        label="Weekday",
        validators=[DataRequired()],
    )
    time = TimeField("Time", format="%H:%M", validators=[DataRequired()], default=datetime.now().time())
    cancel = SubmitField(label="Cancel", render_kw={"formnovalidate": True})
    submit = SubmitField("Create")


class FoodForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    portion_size = IntegerField("Portion size", validators=[DataRequired()])
    amount = IntegerField("Amount", validators=[DataRequired()])
    cancel = SubmitField(label="Cancel", render_kw={"formnovalidate": True})
    submit = SubmitField("Submit")

class FoodDispenseForm(FlaskForm):
    food = SelectField(
        label="Select food to be dispensed",
        validators=[DataRequired()],
        choices=get_food(),
    )
    submit = SubmitField("Dispense now")

class CancelForm(FlaskForm):
    cancel = SubmitField(label="No", render_kw={"formnovalidate": True})
    submit = SubmitField("Yes")
