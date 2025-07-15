from extensions import db

class EmployeeSurvey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer)
    survey_date = db.Column(db.Date)
    answers = db.Column(db.JSON)  # {"q1": "yes", ...}
    score = db.Column(db.Float)
    is_anonymous = db.Column(db.Boolean, default=True) 