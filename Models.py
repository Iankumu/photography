from app import app,db

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:''@localhost:3306/test'

class User(db.Model):
    id = db.Column(db.Integer, primarykey=True)
    username = db.Column(db.String(20), nullable=True)
    FullName = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=True)
    password = db.Column(db.String(120), unique=True, nullable=True)
    photo = db.relationship('Photos', backref=db.backref(lazy='dynamic'))


class Photos(db.Model):
    photoid = db.Column(db.Integer, primarykey=True)
    file_path = db.Column(db.String(120), nullable=True, unique=True)