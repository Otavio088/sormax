from icecreampy.ext.database import db

class ResultProduct(db.Model):
    __tablename__ = 'result_products'
    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, db.ForeignKey('results.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity_production = db.Column(db.Integer, nullable=False)
    total_value = db.Column(db.Numeric(12, 2), nullable=False)
    total_var_cost = db.Column(db.Numeric(12, 2), nullable=False)
    total_fixed_cost = db.Column(db.Numeric(12, 2), nullable=False)

    result = db.relationship('Result', backref='result_products', lazy='select')
    product = db.relationship('Product', backref='result_products', lazy='select')

    def to_json(self):
        return {
            "id": self.id,
            "product_id": self.id_product,
            "product_name": self.product.name,  # se o relacionamento for mapeado
            "quantity_production": self.quantity_production,
            "total_value": self.total_value,
            "total_var_cost": self.total_var_cost,
            "total_fixed_cost": self.total_fixed_cost
        }
