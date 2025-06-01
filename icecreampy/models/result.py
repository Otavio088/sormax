from icecreampy.ext.database import db

class Result(db.Model):
    __tablename__ = 'results'
    id = db.Column(db.Integer, primary_key=True)
    id_user = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    result = db.Column(db.Numeric(10, 2), nullable=False)
