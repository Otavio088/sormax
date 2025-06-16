from icecreampy.ext.database import db

class Result(db.Model):
    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    gross_profit = db.Column(db.Numeric(12, 2), nullable=False)
    net_profit = db.Column(db.Numeric(12, 2), nullable=False)

    user = db.relationship('Account', backref='results', lazy='select')
