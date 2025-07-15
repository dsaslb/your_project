from extensions import db

class StoreConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'))
    is_independent = db.Column(db.Boolean, default=False) 