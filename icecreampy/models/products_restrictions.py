from icecreampy.ext.database import db

class ProductRestriction(db.Model):
    __tablename__ = 'products_restrictions'
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True)
    restriction_id = db.Column(db.Integer, db.ForeignKey('restrictions.id'), primary_key=True)
    quantity_used = db.Column(db.Numeric(10, 2), nullable=False)
