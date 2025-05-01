### <---------- Imports ---------->
# Import Flask modules for routing and template rendering
from flask import render_template, request, jsonify, Blueprint

# Import SQLAlchemy for database handling (not used in this file but included for future use)
from flask_sqlalchemy import SQLAlchemy

# Import the dashboard controller for handling dashboard logic
from dashboard.controller.dashController import dashController

### <---------- Blueprint Setup ---------->
# Create a blueprint for the dashboard routes
dash_bp = Blueprint("dash", __name__)

### <---------- Dashboard Endpoint ---------->
# Define the route for the dashboard (handles both GET and POST requests)
@dash_bp.route('/', methods=['GET', 'POST'])
def inquiry_dashboard():

    # If the request method is POST, process the form submission
    if request.method == 'POST':
        return dashController.dashController()

    # If the request method is GET, render the inquiry form
    return render_template('inquiry_form.html')


