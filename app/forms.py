from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    SelectField,
    IntegerField,
    SelectMultipleField,
    DateTimeField,
)
from wtforms.validators import DataRequired


class ManualFoodForm(FlaskForm):
    submit = SubmitField("Feed")


class TimeTableForm(FlaskForm):
    food = SelectField(label='Select food', validators=[DataRequired()], choices=[(1, 'Food 1'), (2, 'Food 2'), (3, 'Food 3')])
    weekday = SelectMultipleField(
        choices=[
            (0, "Monday"),
            (1, "Tuesday"),
            (2, "Wednesday"),
            (3, "Thursday"),
            (4, "Friday"),
            (5, "Saturday"),
            (6, "Sunday"),
        ],
        label="Weekday",
        validators=[DataRequired()],
    )
    time = DateTimeField("Time", format="%H:%M", validators=[DataRequired()])
    submit = SubmitField("Set")
