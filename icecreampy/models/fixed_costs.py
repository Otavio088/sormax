from icecreampy.ext.database import db

class FixedCost(db.Model):
    __tablename__ = 'fixed_costs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price_month = db.Column(db.Numeric(10, 2), nullable=False)

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "price_month": self.price_month
        }
