import os
from dotenv import load_dotenv
import google.generativeai as genai


class GeminiClient:
    def __init__(self):
        load_dotenv(".env")
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("Missing GEMINI_API_KEY in .env")

        genai.configure(api_key=api_key)

        self.model_name = os.getenv("GEMINI_DEFAULT_MODEL", "gemini-1.5-flash")
        print("MODEL:", self.model_name)
        # Base model (single-turn + chat)
        self.model = genai.GenerativeModel(self.model_name)

        # Keep a chat session around (like your Mistral chat.complete)
        self.chat_session = self.model.start_chat(history=[])

        # Optional: a “search-enabled” model (requires Google Search tool access)
        self.search_model = None
        try:
            self.search_model = genai.GenerativeModel(
                tools=[{"google_search_retrieval": {}}],
                system_instruction=(
                    "Agent able to search information regarding circus and street "
                    "festivals over the web. Use google_search_retrieval for fresh info."
                ),
            )
        except Exception:
            # Library/account may not support the tool; fail soft.
            self.search_model = None

    def chat(self, prompt: str) -> str:
        """
        Multi-turn chat using a persistent session.
        """
        try:
            resp = self.chat_session.send_message(prompt)
            return getattr(resp, "text", str(resp))
        except Exception as e:
            return f"[Gemini chat error] {e}"

    def generate(self, prompt: str) -> str:
        """
        Single-turn completion (no prior history).
        """
        try:
            resp = self.model.generate_content(prompt)
            return getattr(resp, "text", str(resp))
        except Exception as e:
            return f"[Gemini generate error] {e}"

    def search(self, query: str) -> str:
        """
        Web-search assisted response (if the Google Search tool is available).
        """
        if self.search_model is None:
            return ("Search model unavailable. Ensure your account/library supports "
                    "the `google_search_retrieval` tool.")
        try:
            resp = self.search_model.generate_content(query)
            return getattr(resp, "text", str(resp))
        except Exception as e:
            return f"[Gemini search error] {e}"
