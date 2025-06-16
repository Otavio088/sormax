from icecreampy.ext.database import db

class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    profit_percentage = db.Column(db.Numeric(5, 2), nullable=False)

    restrictions = db.relationship(
        'ProductRestriction',
        backref='product',
        lazy='select',
        cascade='all, delete-orphan'
    )

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "profit_percentage": self.profit_percentage,
            "restrictions": [
                { **pr.to_json(), **{ "name": pr.restriction.name,
                                      "unit_type": pr.restriction.unit_type } }
                for pr in self.restrictions
            ]
        }
