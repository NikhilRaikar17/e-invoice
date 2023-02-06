from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    #app.config.from_object("config.DevelopmentConfig")
    app.config['SECRET_KEY'] = b"B!\x1d\xc6\xb8'\xd6\x97\xe9\xa0\xed\xb1\xe3\x00\xa0\xa1"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
        return app
