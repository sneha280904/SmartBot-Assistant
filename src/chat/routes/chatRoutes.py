## working code 

from flask import Blueprint, render_template, request, session, jsonify
from chat.controller.chatController import chatController


chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/", methods=["GET"])
def chatbot():
    session["chat_history"] = []
    session["chat_history"].append({"sender": "bot", "text": "Type HELLO"})
    session["step"] = "greet" 

    return render_template("chat.html", chat_history=session["chat_history"])


@chat_bp.route("/chat", methods=["POST"])
def chat():
    
    return chatController.chatController()

