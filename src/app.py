## working code

from flask import Flask, request, jsonify, session, render_template
import requests
from flask_session import Session
from config import Config  # Import the Config class

# importing my routes or blueprints
# from scrape.routes.scrapeRoutes import scraper_bp
from chat.routes.chatRoutes import chat_bp

# importing database 
from database.database.database import initializeDb

from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow all domains (for testing)

# Load config settings from config.py
app.config.from_object(Config)

# Initialize database connection
initializeDb(app)

# Initialize session
Session(app)

# Register the blueprint
# app.register_blueprint(scraper_bp, url_prefix='/scrape')
app.register_blueprint(chat_bp, url_prefix='/')


# @app.route("/", methods=["GET", "POST"])
# def home():
#     return "Server is running!"

# @app.route("/scrape", methods=["GET", "POST"])
# def scrape():
#     response = requests.get("http://127.0.0.1:5000/scrape")
#     return response.json()

# @app.route("/chat", methods=["POST"])
# def chat():
#     response = requests.post("http://127.0.0.1:5000/chat", json={"message": "Hello"})
#     return response.json()

if __name__ == '__main__':
    app.run(port=5000, debug=True)