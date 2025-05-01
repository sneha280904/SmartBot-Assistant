### <---------- Imports ---------->

# Import necessary modules from Flask
from flask import Blueprint, render_template, request, session, jsonify

# Import the chat controller to handle chat logic
from chat.controller.chatController import chatController


### <---------- Blueprint Setup ---------->

# Create a Blueprint for chat-related routes
chat_bp = Blueprint("chat", __name__)


### <---------- Route: Chatbot Interface (GET) ---------->

@chat_bp.route("/", methods=["GET"])
def chatbot():
    ## Initialize session variables for new chat
    session["chat_history"] = []
    session["chat_history"].append({"sender": "bot", "text": "Type HELLO"})
    session["step"] = "greet"  # Set initial step to greet

    ## Render the chat interface with chat history
    return render_template("chat.html", chat_history=session["chat_history"])


### <---------- Route: Handle Chat Message (POST) ---------->

@chat_bp.route("/chat", methods=["POST"])
def chat():
    ## Delegate handling of user input to the controller
    return chatController.chatController()
