from icecreampy.ext.database import db

class Category(db.Model):
    __tablename__ = 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    days_production = db.Column(db.Numeric(10, 2), nullable=False)

    restrictions = db.relationship(
        'Restriction', 
        backref='category', # Permite acessar a categoria pela restrição (restriction.category)
        lazy='select', # Permite acessar todas as restrições pela categoria (category.restrictions)
        cascade='all, delete' # Todas as restrições associadas a categoria são deletadas quando a mesma é deletada
    )

    def to_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "days_production": self.days_production,
            "restrictions": [r.to_json() for r in self.restrictions]
        }
