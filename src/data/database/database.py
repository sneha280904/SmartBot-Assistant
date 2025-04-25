# Handles database connection and setup.
# Initializes and configures SQLAlchemy.

from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()

def initializeDb(app):
    app.config.from_object(Config)
    db.init_app(app)
    # Import models BEFORE calling db.create_all()
    from data.model.model import User
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully!")  
        except Exception as e:
            print(f"Error creating tables: {e}") 