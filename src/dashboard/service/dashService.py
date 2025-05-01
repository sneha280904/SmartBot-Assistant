### <---------- Imports ---------->
# Import necessary modules from Flask and database
from flask import render_template
from database.database.database import db
from database.model.model import Detail
from database.model.model import Query

# Import datetime for date manipulation
from datetime import datetime, timezone

### <---------- DashService Class ---------->
class dashService:
    # <---------- Constructor ---------->
    def __init__(self):
        print("DashService initialized.")

    # <---------- Main Method to Fetch Data ---------->
    def dashService(self, start_date, end_date):
        # Print the start and end dates for debugging
        print("Start date service: ", start_date)
        print("End date service: ", end_date)

        # <---------- To fetch the Detail table content only ---------->
        # Querying the Detail table for entries within the given date range
        results = db.session.query(Detail).filter(
            Detail.DataTime >= start_date,
            Detail.DataTime <= end_date,
        ).all()

        # Print the fetched results for debugging
        print("Result: ", results)

        # Return the fetched results
        return results
