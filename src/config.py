## <---------- Import Environment Loader ---------->
import os  ## OS module to access environment variables
from dotenv import load_dotenv  ## Load environment variables from a .env file

## <---------- Load Environment Variables ---------->
load_dotenv()  ## Load variables from .env into environment

## <---------- Configuration Class ---------->
class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")  ## Database URI loaded from .env
    SQLALCHEMY_TRACK_MODIFICATIONS = False  ## Disable track modifications to save resources
    SECRET_KEY = os.getenv("SECRET_KEY")  ## Secret key for session and security
    SESSION_TYPE = os.getenv("SESSION_TYPE")  ## Type of session (e.g., filesystem, redis)
    URL = os.getenv("url")  ## Custom application URL (if needed)
    MODEL_NAME = "D:/Coding/Python-Projects/SmartBot-Assistant/src/MLModel/trainedChatbot.pkl"  ## Path to trained chatbot model
    HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")  ## Token for Hugging Face API access

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  ## API key for OpenAI access
