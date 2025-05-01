## <---------- Import Statements ---------->
from flask import Flask, request, jsonify, session, render_template  ## Import Flask and related modules
import requests  ## For making HTTP requests
from flask_session import Session  ## For server-side sessions
from config import Config  ## Import the Config class for configuration settings

## <---------- Import Routes/Blueprints ---------->
# from scrape.routes.scrapeRoutes import scraper_bp  ## Scraper blueprint (currently commented)
from chat.routes.chatRoutes import chat_bp  ## Chatbot blueprint

## <---------- Import Database Connection ---------->
from database.database.database import initializeDb  ## Initialize database connection

from flask_cors import CORS  ## Import CORS for cross-origin requests

## <---------- App Initialization ---------->
app = Flask(__name__)  ## Initialize the Flask app
CORS(app)  ## Enable Cross-Origin Resource Sharing (CORS)

## <---------- Configuration ---------->
app.config.from_object(Config)  ## Load app config from Config class in config.py

## <---------- Database Initialization ---------->
initializeDb(app)  ## Connect to the database using app context

## <---------- Session Management ---------->
Session(app)  ## Enable server-side session handling

## <---------- Register Blueprints ---------->
# app.register_blueprint(scraper_bp, url_prefix='/scrape')  ## Register scraper routes (commented out)
app.register_blueprint(chat_bp, url_prefix='/')  ## Register chatbot routes

## <---------- Run the Flask App ---------->
if __name__ == '__main__':  ## Entry point for running the app
    app.run(port=5000, debug=True)  ## Run app on port 5000 with debug mode enabled
