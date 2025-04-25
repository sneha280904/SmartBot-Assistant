from flask import Flask, request, jsonify, session, render_template
from config import Config
from validation import validation
from data.database.database import db 
from data.model.model import User
import os
import json
import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from sentence_transformers import SentenceTransformer
from difflib import SequenceMatcher
import torch.nn.functional as F

# Global Configuration
class ChatConfig:
    MODEL_PATH = os.path.normpath(Config.LLAMA_MODEL_NAME)
    DATASET_PATH = os.path.join(os.path.dirname(MODEL_PATH), "manualData.json")
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    COURSE_LINKS = {
        "data science": "https://www.talentspiral.com/courses/certification-course-in-data-science",
        "full stack": "https://talentspiral.com/courses/certification-course-in-full-stack-web-development",
        "data analytics": "https://www.talentspiral.com/courses/certification-course-in-data-analytics",
        "digital marketing": "https://www.talentspiral.com/courses/certification-course-in-digital-marketing",
        "software engineering": "https://www.talentspiral.com/courses/certification-course-in-software-engineering",
        "hr": "https://www.talentspiral.com/courses/certification-course-in-hr",
        "ai": "https://www.talentspiral.com/courses/certification-course-in-artificial-intelligence",
        "cloud computing": "https://www.talentspiral.com/courses/certification-course-in-cloud-computing",
        "drone": "https://www.talentspiral.com/courses/drone-training-beginner-certification-program"
    }

# Global Variables
MODEL = None
TOKENIZER = None
QA_DICT = None
SIMILARITY_MODEL = None

# Model Initialization
def initialize_model():
    global MODEL, TOKENIZER, QA_DICT, SIMILARITY_MODEL
    
    if os.path.isdir(ChatConfig.MODEL_PATH):
        print(f"Model found at {ChatConfig.MODEL_PATH}. Loading model and tokenizer...")
        TOKENIZER = AutoTokenizer.from_pretrained(ChatConfig.MODEL_PATH)
        MODEL = AutoModelForCausalLM.from_pretrained(
            ChatConfig.MODEL_PATH,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto"
        )
        MODEL.to(ChatConfig.DEVICE)
        
        if TOKENIZER.pad_token_id is None:
            TOKENIZER.pad_token_id = TOKENIZER.eos_token_id
        MODEL.config.pad_token_id = TOKENIZER.eos_token_id
        print(f"Model loaded on {ChatConfig.DEVICE}")
    else:
        print(f"Warning: Model not found at {ChatConfig.MODEL_PATH}")

    if os.path.exists(ChatConfig.DATASET_PATH):
        with open(ChatConfig.DATASET_PATH, "r", encoding="utf-8") as file:
            dataset = json.load(file)
            QA_DICT = {item.get("question", item.get("q", "")).lower(): item.get("answer", item.get("a", "")) for item in dataset}
        print(f"Dataset loaded with {len(QA_DICT)} question-answer pairs")
    else:
        print(f"Warning: Dataset not found at {ChatConfig.DATASET_PATH}")
    
    SIMILARITY_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    print("Similarity model loaded.")

# Normalize User Input
def normalize_input(user_input):
    user_input = user_input.lower().strip()
    user_input = re.sub(r"\bcost\b", "price", user_input)
    return user_input

# Find Closest Question using Semantic Search
def find_closest_question(user_input, dataset_dict):
    if not SIMILARITY_MODEL or not dataset_dict:
        return None
    questions = list(dataset_dict.keys())
    question_embeddings = SIMILARITY_MODEL.encode(questions)
    input_embedding = SIMILARITY_MODEL.encode(user_input)
    
    question_embeddings_tensor = torch.tensor(question_embeddings).to(ChatConfig.DEVICE)
    input_embedding_tensor = torch.tensor(input_embedding).to(ChatConfig.DEVICE)
    similarities = F.cosine_similarity(input_embedding_tensor.unsqueeze(0), question_embeddings_tensor)
    best_match_idx = similarities.argmax().item()
    
    return questions[best_match_idx] if similarities[best_match_idx] > 0.6 else None

# Remove Repetitive Phrases
def remove_repetitions(text, threshold=0.85):
    sentences = re.split(r'(?<=[.!?]) +|\n', text)
    unique_sentences = []
    for sentence in sentences:
        if not any(SequenceMatcher(None, sentence, s).ratio() > threshold for s in unique_sentences):
            unique_sentences.append(sentence)
    return " ".join(unique_sentences).strip()

# Generate Response with LLM
def getQueryResponse(inputText, chat_history=None):
    try:
        if not MODEL or not TOKENIZER:
            return "Error: Model not initialized"
        
        input_normalized = normalize_input(inputText)
        closest_question = find_closest_question(input_normalized, QA_DICT)
        
        if closest_question:
            response = QA_DICT[closest_question]
        else:
            history_str = "\n".join(chat_history[-5:]) if chat_history else "No prior context."
            prompt = (
                f"[INSTRUCTION] You are a Talent Spiral chatbot. Answer based on history:\n"
                f"{history_str}\n"
                f"[CURRENT QUESTION] {inputText} [END]"
            )
            inputs = TOKENIZER(prompt, return_tensors="pt", padding=True, truncation=True, max_length=512)
            inputs = {key: val.to(ChatConfig.DEVICE) for key, val in inputs.items()}
            
            output = MODEL.generate(
                inputs["input_ids"],
                max_new_tokens=150,
                do_sample=True,
                top_p=0.9,
                temperature=0.7,
                num_beams=5,
                early_stopping=True,
                repetition_penalty=1.2
            )
            response = TOKENIZER.decode(output[0], skip_special_tokens=True).split("[END]")[-1].strip()
            response = remove_repetitions(response)
        
        # Append course links if applicable
        for course, link in ChatConfig.COURSE_LINKS.items():
            if course in input_normalized:
                response += f"\n📌 For more information: <a href='{link}' target= '_blank' >{link}</a>"
                break

        # Clear GPU memory
        if torch.cuda.is_available():
            torch.cuda.empty_cache()  # Added
        
        return response
    except Exception as e:
        return f"Error: {e}"

# Initialize model at startup
initialize_model()

class chatServiceModelFolder:
    def __init__(self):
        pass

    def getChatResponseService(self, inputText):
        if "step" not in session:
            session["step"] = "greet"
            session["chat_history"] = []
            print("Session initialized")

        input_lower = inputText.lower().strip()
        print(f"Current step: {session['step']}, Input: {inputText}")

        if input_lower in ["exit", "bye", "quit"]:
            response = "Goodbye!"
            session.clear()
        elif session["step"] == "greet":
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
            chat_history = [entry["text"] for entry in session["chat_history"]]
            response = getQueryResponse(inputText, chat_history)

        session["chat_history"].append({"sender": "user", "text": inputText})
        session["chat_history"].append({"sender": "bot", "text": response})
        session.modified = True
        print(f"Updated step: {session['step']}, ChatHistory: {session['chat_history']}")
        return render_template("chat.html", chat_history=session["chat_history"])

    def getQueryResponseService(self, inputText):
        if "step" not in session:
            session["step"] = "greet"
            session["chat_history"] = []
            print("Session initialized")

        input_lower = inputText.lower().strip()
        print(f"Current step: {session['step']}, Input: {inputText}")

        if input_lower in ["exit", "bye", "quit"]:
            response = "Goodbye!"
            session.clear()
        elif input_lower in ["hello", "hi", "hey"]:
            response = "Hello! How can I help you?"
        elif session["step"] in ["askQuery", "askQueryAgain"]:
            session["queryCategory"] = inputText
            if all(k in session for k in ["name", "email", "phoneNo"]):
                new_user = User(
                    name=session["name"],
                    email=session["email"],
                    phoneNo=session["phoneNo"],
                    queryDescription=session["queryCategory"]
                )
                db.session.add(new_user)
                db.session.commit()
            chat_history = [entry["text"] for entry in session["chat_history"]]
            response = getQueryResponse(inputText, chat_history)
            session["step"] = "askQueryAgain"
        else:
            chat_history = [entry["text"] for entry in session["chat_history"]]
            response = getQueryResponse(inputText, chat_history)

        session["chat_history"].append({"sender": "user", "text": inputText})
        session["chat_history"].append({"sender": "bot", "text": response})
        session.modified = True
        print(f"Updated step: {session['step']}, ChatHistory: {session['chat_history']}")
        return render_template("chat.html", chat_history=session["chat_history"])

