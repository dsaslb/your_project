from extensions import db


class DeploymentLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(32))
    deployed_at = db.Column(db.DateTime)
    status = db.Column(db.String(16))  # success, failed
    operator = db.Column(db.String(32))
    notes = db.Column(db.Text)
