from app import app, scheduler
from app.models import Timetable
from app.util import dispense_food, calculate_hour, calculate_minutes_remaining, calculate_weekday


@app.before_first_request
def add_jobs():
    times = Timetable.query.all()
    for time in times:
        scheduler.add_job(dispense_food, 'cron', (time.food_id, time.id, 1),
                          day_of_week=calculate_weekday(time.weekday),
                          hour=calculate_hour(time.output_time_minutes), id=str(time.id),
                          minute=calculate_minutes_remaining(time.output_time_minutes))
