### <---------- Imports ---------->
# Import necessary modules from Flask
from flask import jsonify, request, render_template

# Import datetime for date manipulation
from datetime import datetime

# Import the dashboard service to fetch data
from dashboard.service.dashService import dashService

### <---------- Initialize Service ---------->
# Initialize the dashService instance
dashService = dashService()

### <---------- DashController Class ---------->
class dashController:

    # <---------- Dash Controller Method ---------->
    @staticmethod
    def dashController():
        # Fetch the start and end date from the form
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        
        # Convert the string dates into datetime objects
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Print the start and end dates for debugging
        print("Start date: ", start_date)
        print("End date: ", end_date)

        # Fetch the results from the dashService using the provided dates
        results = dashService.dashService(start_date, end_date)
        
        # Print the results fetched from the service
        print("Results in controller: ", results)

        # Render the dashboard page with the fetched results and date range
        return render_template('dashboard.html', results=results, start_date=start_date, end_date=end_date)
