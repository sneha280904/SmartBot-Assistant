import json
import os
import numpy as np
import pickle
import re
import spacy
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load English NLP model
nlp = spacy.load("en_core_web_sm")

def load_dataset(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        dataset = json.load(file)
    return dataset

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
    return text

def prepare_data(dataset):
    questions = []
    answers = []
    for qa in dataset:
        questions.append(preprocess_text(qa["question"]))
        answers.append(qa["answer"])
    return questions, answers

def train_model(dataset_path, model_save_path):
    dataset = load_dataset(dataset_path)
    questions, answers = prepare_data(dataset)
    
    vectorizer = TfidfVectorizer()
    question_vectors = vectorizer.fit_transform(questions)
    
    model_data = {
        "vectorizer": vectorizer,
        "question_vectors": question_vectors,
        "answers": answers,
        "questions": questions
    }
    
    with open(model_save_path, "wb") as model_file:
        pickle.dump(model_data, model_file)
    print(f"Model saved to {model_save_path}")

def load_model(model_path):
    with open(model_path, "rb") as model_file:
        model_data = pickle.load(model_file)
    return model_data

def get_response(user_input, model_data):
    greetings = {
        "hello": "Hello! How can I assist you?",
        "hi": "Hi there! How can I help?",
        "hey": "Hey! What can I do for you?",
        "good morning": "Good morning! How's your day going?",
        "good evening": "Good evening! How can I help?"
    }
    
    user_input = preprocess_text(user_input)
    word_count = len(user_input.split())
    
    if user_input in greetings:
        return greetings[user_input]
    
    vectorizer = model_data["vectorizer"]
    question_vectors = model_data["question_vectors"]
    answers = model_data["answers"]
    questions = model_data["questions"]
    
    # Handle short inputs (1-3 words) with keyword matching
    if word_count <= 3:
        input_keywords = set(user_input.split())
        
        # Check for exact match first
        for idx, question in enumerate(questions):
            if user_input == question:  # Exact match to dataset question
                return answers[idx]
        
        # If no exact match, proceed with keyword scoring
        best_score = 0
        valid_answers = []
        
        for idx, question in enumerate(questions):
            question_keywords = set(question.split())
            common_keywords = input_keywords.intersection(question_keywords)
            score = len(common_keywords)  # Score by keyword overlap
            
            if score > 0:
                if score > best_score:
                    best_score = score
                    valid_answers = [answers[idx]]  # Reset with best match
                elif score == best_score:
                    valid_answers.append(answers[idx])  # Add to ties
        
        if valid_answers:
            return random.choice(valid_answers)  # Randomly pick from best matches
        return "Sorry, I can't understand your query!! Can you rephrase it?"
    
    # Handle longer inputs (>3 words) with ML model
    input_vector = vectorizer.transform([user_input])
    similarities = cosine_similarity(input_vector, question_vectors)[0]
    
    best_match_score = np.max(similarities)
    if best_match_score < 0.3:
        return "Sorry, I can't understand your query!! Can you rephrase it?"
    
    best_match_indices = [i for i, score in enumerate(similarities) if score == best_match_score]
    
    valid_answers = []
    input_keywords = set(user_input.split())
    input_doc = nlp(user_input)
    
    for idx in best_match_indices:
        matched_keywords = set(questions[idx].split())
        common_keywords = input_keywords.intersection(matched_keywords)
        matched_doc = nlp(questions[idx])
        semantic_similarity = input_doc.similarity(matched_doc)
        
        if len(common_keywords) > 0 and semantic_similarity >= 0.3:
            valid_answers.append(answers[idx])
    
    if not valid_answers:
        return "Sorry, I can't understand your query!! Can you rephrase it?"
    
    if len(valid_answers) == 1:
        return valid_answers[0]
    return random.choice(valid_answers)

if __name__ == "__main__":
    dataset_path = "D:\\Coding\\ChatBot\\ML-chatbot\\src\\manualData.json"
    model_save_path = "trainedChatbot.pkl"
    train_model(dataset_path, model_save_path)
    
    model_data = load_model(model_save_path)
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Chatbot: Goodbye!")
            break
        response = get_response(user_input, model_data)
        print(f"Chatbot: {response}")