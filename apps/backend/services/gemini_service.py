import logging
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from rest_framework.exceptions import Throttled

from services.rate_limit import check_llm_rate_limit, increment_llm_call_counter

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()
logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self) -> None:
        load_dotenv(".env")
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("Missing GEMINI_API_KEY in .env")

        self.client = genai.Client()
        # Define the grounding tool
        self.grounding_tool = types.Tool(google_search=types.GoogleSearch())
        # Configure generation settings
        self.config = types.GenerateContentConfig(tools=[self.grounding_tool])

    def search(self, query: str, tenant_schema: str) -> str:
        allowed, _remaining = check_llm_rate_limit(tenant_schema)
        logger.info(f"user {tenant_schema} rate: {allowed}, left: {_remaining}")
        if not allowed:
            raise Throttled(detail="Daily LLM generation limit reached. Try again tomorrow.")
        try:
            resp = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=query,
                config=self.config,
            )
            new_count = increment_llm_call_counter(tenant_schema)  # noqa
            logger.info(f"user {tenant_schema} new LLM rate: {new_count}")
            return getattr(resp, "text", str(resp))
        except Exception as e:
            return f"[Gemini chat error] {e}"
