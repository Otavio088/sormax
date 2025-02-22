from icecreampy.ext.database import db

class accounts(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), nullable=False)

    def to_json(self):
        return {"id": self.id, "username": self.username, "password": self.password, "email": self.email}

    # with app.app_context():
    #     db.create_all()