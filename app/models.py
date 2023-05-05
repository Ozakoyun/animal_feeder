from app import db


class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    portion_size = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DateTime, index=True, nullable=False)
    food_dispensed = db.relationship(
        "FoodDispensed", backref="food_dispensed", lazy="dynamic"
    )
    timetable = db.relationship(
        "Timetable", backref="timetable", lazy="dynamic", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return "<id {}: Food {}, portion_size: {}, amount: {}, created at: {}, food_dispensed: {}, timetable: {}>".format(
            self.id,
            self.name,
            self.portion_size,
            self.amount,
            self.created,
            self.food_dispensed,
            self.timetable,
        )


class FoodDispensed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount_dispensed = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    trigger = db.Column(db.Integer, nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey("food.id"), nullable=True)
    timetable_id = db.Column(db.Integer, db.ForeignKey("timetable.id"), nullable=True)

    def __repr__(self):
        return "<id {}: FoodDispensed {}, amount_dispensed: {}, created at: {}, trigger: {}, timetable_id: {}>".format(
            self.id,
            self.food_id,
            self.amount_dispensed,
            self.created,
            self.trigger,
            self.timetable_id,
        )


class Timetable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    output_time_minutes = db.Column(db.Integer, nullable=False) # probably save as seconds since midnight
    weekday = db.Column(db.String, nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey("food.id"), nullable=False)
    food_dispensed = db.relationship(
        "FoodDispensed", backref="timetable_dispensed", lazy="dynamic"
    )

    def __repr__(self):
        return "<id {}: output_time: {}, weekday: {}, food_id: {}, food_dispensed>".format(
            self.id, self.output_time_minutes, self.weekday, self.food_id, self.food_dispensed
        )
