from dotenv import load_dotenv
from google import genai
import ollama
import os

def prompt_model(model: str, prompt: str, temperature=None) -> str :
	
	load_dotenv()
	ollamalist = ["phi3", "llama3.1", "deepseek-r1", "gemma4:e2b", "llama3.2:3b"]
	geminilist = ["gemini-3-flash-preview", "gemini-2.5-flash", "gemini-2.5-flash-lite"]
	allmodels = ollamalist + geminilist

	client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
	try:
		if model not in allmodels:
			raise ValueError(f"Model {model} not found in available models.")
		if (model.startswith("gemini")):
			print(f"Asking model: {model}")
			response = client.models.generate_content(model=model, contents=prompt, config={'temperature':temperature}).text
		else:
			print(f"Asking model: {model}")
			response = ollama.generate(model=model, prompt=prompt, stream=False, options={'temperature':temperature})['response']
		return response

			# for m in ollamalist:
			# 	try:
			# 		print(f"Testing ollama model: {m}")
			# 		response = ollama.generate(model=m, prompt=prompt, options={"num_predict": 100})
			# 		return response['response']
			# 	except Exception as e:
			# 		print(f"An error occurred with model {m}: {e}")
			# 		continue
			# for g in geminilist:
			# 	try:
			# 		print(f"Testing gemini model: {g}")
			# 		response = client.models.generate_content(model=g, contents=prompt)
			# 		return response.text
			# 	except Exception as e:
			# 		print(f"An error occurred with model {g}: {e}")
			# 		continue
			# return ("All models failed to generate a response.")
	except Exception as e:
		return (f"An error occurred while generating response: {e}")
