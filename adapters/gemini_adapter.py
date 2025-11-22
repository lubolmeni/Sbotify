import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def crear_modelo(instrucciones):
    model = genai.GenerativeModel(model_name='gemini-2.5-flash', system_instruction=instrucciones)
    return model

def preguntar_gemini(pregunta, instrucciones=None, estructura_salida=None):
    model = crear_modelo(instrucciones)
    generation_config = genai.GenerationConfig(response_mime_type='application/json', response_schema=estructura_salida) if estructura_salida else None
    response = model.generate_content(pregunta, generation_config=generation_config)
    return response.text

