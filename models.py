from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    original_filename = db.Column(db.String(200), nullable=False)
    result_path = db.Column(db.String(200), nullable=False)
    result_type = db.Column(db.String(20), nullable=False)
    result_ext = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
