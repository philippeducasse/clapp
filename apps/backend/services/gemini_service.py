import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

class GeminiClient:
    def __init__(self):
        load_dotenv(".env")
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("Missing GEMINI_API_KEY in .env")

        self.client=genai.Client()
        # Define the grounding tool
        self.grounding_tool = types.Tool(google_search=types.GoogleSearch())
        # Configure generation settings
        self.config = types.GenerateContentConfig(tools=[self.grounding_tool])


    def search(self, query: str) -> str:
        try:
            resp = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=query,
                config=self.config,
            )
            return getattr(resp, "text", str(resp))
        except Exception as e:
            return f"[Gemini chat error] {e}"
