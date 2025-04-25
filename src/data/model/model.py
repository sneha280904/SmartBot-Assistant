# This file defines database tables and relationships using SQLAlchemy 
# Represents the database schema in Python classes.

from data.database.database import db

class User(db.Model):
    __tablename__ = 'userDetail'
    userId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phoneNo = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    queryDescription = db.Column(db.String(100))
