from icecreampy.ext.database import db

class ResultProduct(db.Model):
    __tablename__ = 'result_products'
    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, db.ForeignKey('results.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity_production = db.Column(db.Integer, nullable=False)
    total_value = db.Column(db.Numeric(12, 2), nullable=False)

    def to_json(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "product_name": self.product.name,
            "quantity_production": self.quantity_production,
            "total_value": float(self.total_value)
        }
