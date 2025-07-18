from extensions import db


class BrandHierarchy(db.Model):
    __tablename__ = 'brand_hierarchy'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    is_headquarter = db.Column(db.Boolean, default=False)


class StoreHierarchy(db.Model):
    __tablename__ = 'store_hierarchy'
    id = db.Column(db.Integer, primary_key=True)
    brand_id = db.Column(db.Integer, db.ForeignKey("brand_hierarchy.id"))
    name = db.Column(db.String(64))
