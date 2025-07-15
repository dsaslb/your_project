from extensions import db

class CustomerFeedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer)
    store_id = db.Column(db.Integer)
    nps_score = db.Column(db.Integer)  # 0~10
    review = db.Column(db.Text)
    created_at = db.Column(db.DateTime) 