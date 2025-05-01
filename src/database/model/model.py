### <---------- Imports ---------->
# Import necessary modules from SQLAlchemy and datetime
from database.database.database import db
from datetime import datetime, timezone

### <---------- Detail Table Definition ---------->
# Represents the userDetails table in the database
class User(db.Model):
    __tablename__ = 'SmartBotChatUserDetails'  # Table name in the database

    ### <---------- Columns of the userDetails Table ---------->
    userId = db.Column(db.Integer, primary_key=True)  # Primary key for userId
    
    name = db.Column(db.String(100))  # User name (max length 100)
    email = db.Column(db.String(100))  # User email (max length 100)
    phoneNo = db.Column(db.String(20))  # User phone number (max length 20)

    query_description = db.Column(db.String(1000))  # User's first query category (max length 1000)

    DateTime = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),  # Default to current UTC time
        nullable=False  # This field cannot be null
    )
