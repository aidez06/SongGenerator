import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from dotenv import load_dotenv
import os


load_dotenv()

def prompt(message:str):
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    generation_config = {
    "temperature": float(os.getenv("GENERATIVE_TEMPERATURE")),
    "top_p": float(os.getenv("GOOGLE_TOP_P")),
    "top_k": int(os.getenv("GOOGLE_TOP_K")),
    "max_output_tokens": int(os.getenv("GOOGLE_MAX_OUT_TOKEN")),
    "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
    model_name=os.getenv("GOOGLE_AI_MODEL"),
    generation_config=generation_config,
    safety_settings={
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT:HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    }
    )


    chat_session = model.start_chat(
    history=[
    ]
    )

    response = chat_session.send_message(message)

    return response.text