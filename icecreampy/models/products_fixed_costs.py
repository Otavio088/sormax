from icecreampy.ext.database import db

class ProductFixedCost(db.Model):
    __tablename__ = 'products_fixed_costs'
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), primary_key=True)
    fixed_cost_id = db.Column(db.Integer, db.ForeignKey('fixed_costs.id'), primary_key=True)
    quantity_used = db.Column(db.Numeric(10, 2), nullable=False)

    fixedCost = db.relationship(
        'FixedCost',
        backref='fixed_costs',
        lazy='joined'
    )

    def to_json(self):
        return {
            "fixed_cost_id": self.fixed_cost_id,
            "quantity_used": self.quantity_used
        }