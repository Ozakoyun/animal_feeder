from app import db


class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    portion_size = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DateTime, index=True, nullable=False)
    food_dispensed = db.relationship(
        "FoodDispensed", backref="food_dispensed", lazy="dynamic"
    )

    def __repr__(self):
        return "<id {}: Food {}, portion_size: {}, amount: {}, created at: {}>".format(
            self.id, self.name, self.portion_size, self.amount, self.created
        )


class FoodDispensed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount_dispensed = db.Column(db.Integer, nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    trigger = db.Column(db.Integer, nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey("food.id"), nullable=False)
    tiemtable_id = db.Column(db.Integer, db.ForeignKey("timetable.id"), nullable=True)

    def __repr__(self):
        return "<id {}: FoodDispensed {}, amount_dispensed: {}, created at: {}>".format(
            self.id, self.food_id, self.amount_dispensed, self.created
        )
    
class Timetable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    output_time = db.Column(db.DateTime, nullable=False)
    weekday = db.Column(db.Integer, nullable=False)
    food_dispensed = db.relationship("FoodDispensed", backref="timetable_dispensed", lazy="dynamic")

    def __repr__(self):
        return "<id {}: Timetable {}, output_time: {}, weekday: {}>".format(
            self.id, self.food_id, self.output_time, self.weekday
        )
