### <---------- Imports ---------->
# Import SQLAlchemy for database ORM
from flask_sqlalchemy import SQLAlchemy

# Import configuration settings
from config import Config

### <---------- Database Initialization ---------->
# Create an instance of SQLAlchemy for handling the database connection
db = SQLAlchemy()

### <---------- Function to Initialize Database ---------->
def initializeDb(app):
    ## Set app configuration from Config class
    app.config.from_object(Config)
    ## Bind SQLAlchemy instance with the Flask app
    db.init_app(app)
    
    ## Import database models (must be done after app and db setup)
    from database.model.model import User

    ### <---------- Create Tables and Handle Errors ---------->
    # Push an application context to use db.create_all()
    with app.app_context():
        try:
            # Create database tables for all imported models
            db.create_all()
            ## Success message after creating tables
            print("Database tables created successfully!") 
        except Exception as e:
            ## Print error message if table creation fails
            print(f"Error creating tables: {e}") 
