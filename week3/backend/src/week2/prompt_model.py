from dotenv import load_dotenv
from google import genai
import ollama
import os

load_dotenv()

OLLAMA_PORT = int(os.getenv("OLLAMA_PORT", "11434"))
OLLAMA_BASE_URL = f"http://ollama:{OLLAMA_PORT}"

ollamalist = ["phi3", "llama3.1", "deepseek-r1", "gemma4:e2b", "llama3.2:3b"]
geminilist = ["gemini-3-flash-preview", "gemini-2.5-flash", "gemini-2.5-flash-lite"]
allmodels = ollamalist + geminilist


def prompt_model(model: str, prompt: str, temperature=None) -> str:
    try:
        if model not in allmodels:
            raise ValueError(f"Model {model} not found in available models.")

        if model.startswith("gemini"):
            print(f"Asking model: {model}")
            client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
            response = client.models.generate_content(
                model=model, contents=prompt, config={"temperature": temperature}
            ).text
        else:
            print(f"Asking model: {model} at URL {OLLAMA_BASE_URL}")
            client = ollama.Client(host=OLLAMA_BASE_URL)
            response = client.generate(
                model=model,
                prompt=prompt,
                stream=False,
                options={"temperature": temperature},
            )["response"]
        return response

    except Exception as e:
        print(f"An error occurred while generating response {e}")
        return None
