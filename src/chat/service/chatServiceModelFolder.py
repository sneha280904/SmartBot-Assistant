## <---------- Imports and Dependencies ---------->
from flask import session, render_template  ## Flask session and template rendering
from config import Config  ## Custom configuration class
from validation import validation  ## Email and phone validation utility
from database.database.database import db  ## SQLAlchemy DB instance
from database.model.model import User  ## SQLAlchemy model for User
import os  ## Operating system utilities
import json  ## JSON file handling
import re  ## Regular expressions
import torch  ## PyTorch for model handling
from transformers import AutoTokenizer, AutoModelForCausalLM  ## HuggingFace Transformers
from sentence_transformers import SentenceTransformer  ## Semantic similarity model
from difflib import SequenceMatcher  ## For sentence similarity
import torch.nn.functional as F  ## Functional API for cosine similarity

## <---------- Configuration Class ---------->
class ChatConfig:
    MODEL_PATH = os.path.normpath(Config.MODEL_NAME)  ## Normalize model path from config
    DATASET_PATH = os.path.join(os.path.dirname(MODEL_PATH), "D:/Coding/Python-Projects/SmartBot-Assistant/src/dataset/dataset.json")  ## Path to dataset
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")  ## Use GPU if available

## <---------- Global Variables ---------->
MODEL = None  ## Placeholder for LLM model
TOKENIZER = None  ## Placeholder for tokenizer
QA_DICT = None  ## Question-answer dictionary
SIMILARITY_MODEL = None  ## Sentence similarity model

## <---------- Model Initialization Function ---------->
def initialize_model():
    global MODEL, TOKENIZER, QA_DICT, SIMILARITY_MODEL

    if os.path.isdir(ChatConfig.MODEL_PATH):  ## Check if model directory exists
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

    if os.path.exists(ChatConfig.DATASET_PATH):  ## Load dataset
        with open(ChatConfig.DATASET_PATH, "r", encoding="utf-8") as file:
            dataset = json.load(file)
            QA_DICT = {item.get("question", item.get("q", "")).lower(): item.get("answer", item.get("a", "")) for item in dataset}
        print(f"Dataset loaded with {len(QA_DICT)} question-answer pairs")
    else:
        print(f"Warning: Dataset not found at {ChatConfig.DATASET_PATH}")
    
    SIMILARITY_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    print("Similarity model loaded.")

## <---------- Normalize Input ---------->
def normalize_input(user_input):
    user_input = user_input.lower().strip()
    user_input = re.sub(r"\bcost\b", "price", user_input)  ## Normalize keywords
    return user_input

## <---------- Semantic Similarity Search ---------->
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
    
    return questions[best_match_idx] if similarities[best_match_idx] > 0.6 else None  ## Threshold for match

## <---------- Remove Redundant Sentences ---------->
def remove_repetitions(text, threshold=0.85):
    sentences = re.split(r'(?<=[.!?]) +|\n', text)
    unique_sentences = []
    for sentence in sentences:
        if not any(SequenceMatcher(None, sentence, s).ratio() > threshold for s in unique_sentences):
            unique_sentences.append(sentence)
    return " ".join(unique_sentences).strip()

## <---------- Generate Response with LLM ---------->
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
                f"[INSTRUCTION] You are a conversational chatbot. Answer based on history:\n"
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

        if torch.cuda.is_available():
            torch.cuda.empty_cache()  ## Clear GPU memory
        
        return response
    except Exception as e:
        return f"Error: {e}"

## <---------- Model Initialization Call ---------->
initialize_model()

## <---------- Chat Service Class ---------->
class chatServiceModelFolder:
    def __init__(self):
        pass

    ## <---------- Main Chat Response ---------->
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

    ## <---------- Query-Only Chat Response ---------->
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
