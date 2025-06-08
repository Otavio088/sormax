from icecreampy.ext.database import db

class ResultProduct(db.Model):
    __tablename__ = 'result_products'
    id = db.Column(db.Integer, primary_key=True)
    id_result = db.Column(db.Integer, db.ForeignKey('results.id'), nullable=False)
    id_product = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity_production = db.Column(db.Integer, nullable=False)
    total_value = db.Column(db.Numeric(10, 2), nullable=False)
