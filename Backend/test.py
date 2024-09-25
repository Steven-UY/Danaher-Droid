from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')

# Check if the API key was retrieved successfully
if openai_api_key is None:
    raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

# Initialize the ChatOpenAI object with the API key
llm = ChatOpenAI(openai_api_key=openai_api_key)
llm.invoke("Hello, world!")

