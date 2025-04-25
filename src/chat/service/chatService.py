## working code 

from flask import Flask, request, jsonify, session, render_template
from config import Config
from validation import validation
# import ollama
import pickle
import os
from data.database.database import db 
from data.model.model import User

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class chatService:
    def __init__(self):
        # Load trained chatbot model using path from Config
        model_path = Config.LLAMA_MODEL_NAME  # Load from config
        if os.path.exists(model_path):
            with open(model_path, "rb") as f:
                self.model = pickle.load(f)
        else:
            self.model = None
            print(f"Warning: Model not found at {model_path}. Train the model first.")

    def getQueryResponse(inputText):
        try:
            # app.config.from_object(Config)
            chat_service = chatService()
            if chat_service.model:
                
                if chat_service.model:
                    vectorizer = chat_service.model["vectorizer"]
                    question_vectors = chat_service.model["question_vectors"]
                    answers = chat_service.model["answers"]

                    input_vector = vectorizer.transform([inputText])
                    similarities = cosine_similarity(input_vector, question_vectors)
                    best_match_idx = np.argmax(similarities)

                    response = answers[best_match_idx]
                else:
                    response = "Error: Model not found."


            return response
        except Exception as e:
            return f"Error: {e}"
        
    def getChatResponseService(self, inputText):
        # Handle conversation steps
        if "step" not in session:
            session["step"] = "greet"

        if session["step"] == "greet":
            response = "Hello! What is your name?"
            session["step"] = "askName"
            # return response

        elif session["step"] == "askName":
            session["name"] = inputText
            response = f"Nice to meet you, {inputText}! Please enter your email."
            session["step"] = "askEmail"
            # return response

        elif session["step"] == "askEmail":
            if validation.validateEmail(inputText):
                session["email"] = inputText
                response = "Thanks! Now, enter your phone number."
                session["step"] = "askPhoneNumber"
            else:
                response = "Please enter a valid email address."
            # return response

        elif session["step"] == "askPhoneNumber":
            if validation.validatePhoneNumber(inputText):
                session["phoneNo"] = inputText
                response = "Now, you can ask your queries..."
                session["step"] = "askQuery"
            else:
                response = "Please enter a valid phone number."
            # return response
        
        else:
            response = "Error in get chat Response Service Function!"
            # return response
        
        # Store messages in chat history
        print(f"session: {session['step']}")

        session["chat_history"].append({"sender": "user", "text": inputText})
        session["chat_history"].append({"sender": "bot", "text": response})
        # session["chat_history"].append({"sender":templates/chat.html: "bot", "text": response})
        session.modified = True
        # Pass chat history to template to display it
        print(f"ChatHistory: {session['chat_history']}")
        return render_template("chat.html", chat_history=session["chat_history"])
        # return response

    
    def getQueryResponseService(self, inputText):
        if session["step"] == "askQuery":
            session["queryCategory"] = inputText
            new_user = User(
                name=session["name"],
                email=session["email"],
                phoneNo=session["phoneNo"],
                queryDescription=session["queryCategory"]
            )
            db.session.add(new_user)
            db.session.commit()
            response = chatService.getQueryResponse(inputText)
            session["step"] = "askQueryAgain"
            # return response

        elif session["step"] == "askQueryAgain":
            session["query_category"] = inputText
            response = chatService.getQueryResponse(inputText)
            session["step"] = "askQueryAgain"
            # return response

        else:
            response = "Error in Get Query Response Service Function!"
            # return response

        # Store messages in chat history
        session["chat_history"].append({"sender": "user", "text": inputText})
        session["chat_history"].append({"sender": "bot", "text": response})
        # session["chat_history"].append({"sender":templates/chat.html: "bot", "text": response})
        session.modified = True
        # Pass chat history to template to display it
        return render_template("chat.html", chat_history=session["chat_history"])
        # return response