

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY")
    SESSION_TYPE = os.getenv("SESSION_TYPE")
    URL = os.getenv("url")
    MODEL_NAME = "D:/Coding/Python-Projects/SmartBot-Assistant/src/MLModel/trainedChatbot.pkl"
    HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


