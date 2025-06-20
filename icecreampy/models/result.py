from icecreampy.ext.database import db

class Result(db.Model):
    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    gross_profit = db.Column(db.Numeric(12, 2), nullable=False)
    net_profit = db.Column(db.Numeric(12, 2), nullable=False)
    total_variable_costs = db.Column(db.Numeric(12, 2), nullable=False)
    total_fixed_costs = db.Column(db.Numeric(12, 2), nullable=False)

    result_products = db.relationship('ResultProduct', backref='result', lazy='select')

    def to_json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "gross_profit": float(self.gross_profit),
            "net_profit": float(self.net_profit),
            "total_variable_costs": float(self.total_variable_costs),
            "total_fixed_costs": float(self.total_fixed_costs),
            "products": [rp.to_json() for rp in self.result_products]
        }
