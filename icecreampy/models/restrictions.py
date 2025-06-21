from icecreampy.ext.database import db

class Restriction(db.Model):
    __tablename__ = 'restrictions'
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    unit_type = db.Column(db.String(8), nullable=False)
    quantity_available = db.Column(db.Numeric(10, 2), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "unit_type": self.unit_type,
            "quantity_available": self.quantity_available,
            "unit_price": self.unit_price
        }
