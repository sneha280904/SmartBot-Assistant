## working code 

from flask import Blueprint, render_template, request, session, jsonify
from chat.controller.chatController import chatController


chat_bp = Blueprint("chat", __name__)

@chat_bp.route("/", methods=["GET"])
def chatbot():
    session["chat_history"] = []
    session["chat_history"].append({"sender": "bot", "text": "Type HELLO"})
    session["step"] = "greet" 
    # session["query_category"] = ""
    # session["query_subcategory"] = ""

    return render_template("chat.html", chat_history=session["chat_history"])

@chat_bp.route("/chat", methods=["POST"])
def chat():
    # data = request.json
    # user_message = data.get("message", "")

    # if not user_message:
    #     return jsonify({"response": "Invalid input!"}), 400

    # response_text = getChatRsponse(user_message)
    # return jsonify({"response": response_text})
    return chatController.chatController()

# from flask import Blueprint, request, render_template, session
# from ..service.chatServiceModelFolder import chatServiceModelFolder  # Import from sibling services folder

# chat_bp = Blueprint('chat', __name__)

# @chat_bp.route('/')
# def index():
#     return render_template("chat.html", chat_history=session["chat_history"])

# @chat_bp.route('/chat', methods=['POST'])
# def chat():
#     chat_service = chatServiceModelFolder()  # Instantiate the class
#     input_text = request.form.get('message')
#     if session.get("step") in ["askQuery", "askQueryAgain"]:
#         return chat_service.getQueryResponseService(input_text)
#     return chat_service.getChatResponseService(input_text)