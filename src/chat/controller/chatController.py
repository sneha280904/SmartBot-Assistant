### <---------- Imports ---------->

# Import Flask modules for session handling, redirects, and request parsing
from flask import session, redirect, url_for, jsonify, request

# Import the chat service logic
# from chat.service.chatService import chatService  # (Commented out if unused)
from chat.service.chatServiceModelFolder import chatServiceModelFolder


### <---------- Initialize Chat Service ---------->

# Create an instance of the chat service
chatServiceModelFolder = chatServiceModelFolder()


### <---------- ChatController Class ---------->

class chatController:
    
    ### <---------- Constructor ----------> 
    def __init__(self):
        pass

    ### <---------- Chat Controller Method ---------->
    @staticmethod
    def chatController():
        ## Check if the request is a JSON API call
        if request.is_json:
            data = request.get_json()
            print("data = ", data)
            inputText = data.get("message", "").strip()
        else:
            ## Otherwise, fetch input text from HTML form
            inputText = request.form.get("message", "").strip()

        ## Redirect to index if message is empty
        if not inputText:
            return redirect(url_for("index"))

        ### <---------- Session State Initialization ---------->
        ## Create chat history and step if not already set in session
        if "chat_history" not in session:
            session["chat_history"] = []
            session["step"] = "greet"

        ## Initialize response
        response = ""
        print(f"session: {session['step']}")

        ### <---------- Step-Based Chat Routing ---------->
        ## Handle greeting and user info collection steps
        if session["step"] in {"greet", "askName", "askPhoneNumber", "askEmail"}:
            print(f"session: {session['step']}")
            return chatServiceModelFolder.getChatResponseService(inputText)

        ## Handle query-related steps
        if session["step"] in {"askQuery", "askQueryAgain"}:
            return chatServiceModelFolder.getQueryResponseService(inputText)

        ## Fallback: return empty JSON response
        return jsonify(response)
