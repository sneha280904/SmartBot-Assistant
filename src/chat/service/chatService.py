### <---------- Imports ---------->

# Flask modules
from flask import session, render_template

# Configuration and validation
from config import Config
from validation import validation

# Database imports
from database.database.database import db 
from database.model.model import User

# File and model handling
import pickle
import os

# ML and similarity
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Time for database record
from datetime import datetime, timezone


### <---------- Chat Service Class ---------->

class chatService:
    def __init__(self):
        # Load trained chatbot model using path from Config
        model_path = Config.MODEL_NAME
        if os.path.exists(model_path):
            with open(model_path, "rb") as f:
                self.model = pickle.load(f)
        else:
            self.model = None
            print(f"Warning: Model not found at {model_path}. Train the model first.")

    
    ### <---------- Internal Method: Get Best Match Response ---------->
    @staticmethod
    def getQueryResponse(inputText):
        try:
            # Use existing model instance if loaded
            service = chatService()
            if service.model:
                vectorizer = service.model["vectorizer"]
                question_vectors = service.model["question_vectors"]
                answers = service.model["answers"]

                input_vector = vectorizer.transform([inputText])
                similarities = cosine_similarity(input_vector, question_vectors)
                best_match_idx = np.argmax(similarities)

                response = answers[best_match_idx]
            else:
                response = "Error: Model not found."
            return response
        except Exception as e:
            return f"Error: {e}"


    ### <---------- Handle Greeting and Initial Conversation Steps ---------->
    def getChatResponseService(self, inputText):
        # Ensure step and chat_history exist in session
        if "step" not in session:
            session["step"] = "greet"
        if "chat_history" not in session:
            session["chat_history"] = []

        if session["step"] == "greet":
            response = "Hello! What is your name?"
            session["step"] = "askName"

        elif session["step"] == "askName":
            session["name"] = inputText
            response = f"Nice to meet you, {inputText}! Please enter your email."
            session["step"] = "askEmail"

        elif session["step"] == "askEmail":
            if validation.validateEmail(inputText):
                session["email"] = inputText
                response = "Thanks! Now, enter your phone number."
                session["step"] = "askPhoneNumber"
            else:
                response = "Please enter a valid email address."

        elif session["step"] == "askPhoneNumber":
            if validation.validatePhoneNumber(inputText):
                session["phoneNo"] = inputText
                response = "Now, you can ask your queries..."
                session["step"] = "askQuery"
            else:
                response = "Please enter a valid phone number."

        else:
            response = "Error in get chat Response Service Function!"

        # Store message and bot response in chat history
        session["chat_history"].append({"sender": "user", "text": inputText})
        session["chat_history"].append({"sender": "bot", "text": response})
        session.modified = True

        # Debugging outputs
        print(f"session: {session['step']}")
        print(f"ChatHistory: {session['chat_history']}")

        # Render updated chat history
        return render_template("chat.html", chat_history=session["chat_history"])


    ### <---------- Handle Query Processing and Database Storage ---------->
    def getQueryResponseService(self, inputText):
        if "chat_history" not in session:
            session["chat_history"] = []

        if session["step"] == "askQuery":
            session["queryCategory"] = inputText

            # Store user data into the database
            new_user = User(
                name=session["name"],
                email=session["email"],
                phoneNo=session["phoneNo"],
                queryDescription=session["queryCategory"],
                DateTime=datetime.now(timezone.utc)  # Store UTC time
            )
            db.session.add(new_user)
            db.session.commit()

            response = chatService.getQueryResponse(inputText)
            session["step"] = "askQueryAgain"

        elif session["step"] == "askQueryAgain":
            session["queryCategory"] = inputText
            response = chatService.getQueryResponse(inputText)
            session["step"] = "askQueryAgain"

        else:
            response = "Error in Get Query Response Service Function!"

        # Store message and bot response in chat history
        session["chat_history"].append({"sender": "user", "text": inputText})
        session["chat_history"].append({"sender": "bot", "text": response})
        session.modified = True

        # Render updated chat history
        return render_template("chat.html", chat_history=session["chat_history"])
