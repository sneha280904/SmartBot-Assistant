## working code

from flask import session, redirect, url_for, jsonify, request
# from chat.service.chatService import chatService
from chat.service.chatServiceModelFolder import chatServiceModelFolder

# chatService = chatService()
chatServiceModelFolder = chatServiceModelFolder()

class chatController:
    def __init__(self):
        pass

    def chatController():
        # Check if request has JSON data (API call)
        if request.is_json:
            data = request.get_json()
            print("data = ",data)
            inputText = data.get("message", "").strip()
        else:
            # Otherwise, get data from form (HTML form submission)
            inputText = request.form.get("message", "").strip()

        if not inputText:
            return redirect(url_for("index"))
        
        # Initialize chat history in session if not already present
        if "chat_history" not in session:
            session["chat_history"] = []
            session["step"] = "greet"
        
        response = ""
        print(f"session: {session['step']}")
        
        if session["step"] in {"greet", "askName", "askPhoneNumber", "askEmail"}:
            print(f"session: {session['step']}")
            # return chatService.getChatResponseService(inputText)
            return chatServiceModelFolder.getChatResponseService(inputText)
        
        
        if session["step"] in {"askQuery", "askQueryAgain"}:
            # return chatService.getQueryResponseService(inputText)
            return chatServiceModelFolder.getQueryResponseService(inputText)
        
        return jsonify(response)
    
    