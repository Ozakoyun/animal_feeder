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
    """
    Enables the sending of the form data with a submit field.
    :param FlaskForm: a required (by the library) parameter to process a form
    """
    submit = SubmitField("Feed")


class TimeTableForm(FlaskForm):
    """
    Represents the form for creating a timetable.
    Enables the sending of the form data with a submit field.
    :param FlaskForm: a required (by the library) parameter to process a form
    """
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
    """
    Represents the form for creating a food.
    Enables the sending of the form data with a submit field.
    :param FlaskForm: a required (by the library) parameter to process a form
    """
    name = StringField("Name", validators=[DataRequired()])
    portion_size = IntegerField("Portion size", validators=[DataRequired()])
    amount = IntegerField("Amount", validators=[DataRequired()])
    cancel = SubmitField(label="Cancel", render_kw={"formnovalidate": True})
    submit = SubmitField("Submit")

class FoodDispenseForm(FlaskForm):
    """
    Represents the form for choosing the food to be dispensed.
    Enables the sending of the form data with a submit field.
    :param FlaskForm: a required (by the library) parameter to process a form
    """
    food = SelectField(
        label="Select food to be dispensed",
        validators=[DataRequired()],
        choices=get_food(),
    )
    submit = SubmitField("Dispense now")

class CancelForm(FlaskForm):
    """
    Represents the form for deleting a timetable or food.
    Enables the sending of the form data with a submit field.
    :param FlaskForm: a required (by the library) parameter to process a form
    """
    cancel = SubmitField(label="No", render_kw={"formnovalidate": True})
    submit = SubmitField("Yes")
