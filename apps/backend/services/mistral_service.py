# mypy: ignore-errors

import json
import logging
import os
import threading

from mistralai import ConversationResponse, Mistral
from pydantic import ValidationError
from rest_framework.exceptions import Throttled

from .rate_limit import check_llm_rate_limit, increment_llm_call_counter

logger = logging.getLogger(__name__)


class MistralClient:
    # The web search agent is a remote resource: create it once per process
    # (or reuse MISTRAL_SEARCH_AGENT_ID) instead of once per request.
    _search_agent_id: str | None = None
    _search_agent_lock = threading.Lock()

    def __init__(self) -> None:
        self.client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
        self.model = os.getenv("MISTRAL_DEFAULT_MODEL")
        self.fallback_model = os.getenv("MISTRAL_FALLBACK_MODEL", "mistral-medium-latest")

    @property
    def search_agent_id(self) -> str:
        cls = type(self)
        if cls._search_agent_id is None:
            with cls._search_agent_lock:
                if cls._search_agent_id is None:
                    cls._search_agent_id = (
                        os.getenv("MISTRAL_SEARCH_AGENT_ID") or self._create_search_agent()
                    )
        return cls._search_agent_id

    def _create_search_agent(self) -> str:
        agent = self.client.beta.agents.create(
            model="mistral-medium-2508",
            description="Agent able to search information regarding circus and street festivals over the web",
            name="Websearch Agent",
            instructions="You have the ability to perform web searches with `web_search` to find up-to-date information.",
            tools=[{"type": "web_search"}],
            completion_args={
                "temperature": 0.3,
                "top_p": 0.95,
            },
        )
        logger.info("Created Mistral search agent %s", agent.id)
        return agent.id

    def chat(self, prompt: str, tenant_schema: str, json_mode: bool = False) -> str:
        allowed, _remaining = check_llm_rate_limit(tenant_schema)
        logger.info(f"user {tenant_schema} rate: {allowed}, left: {_remaining}")
        if not allowed:
            raise Throttled(detail="Daily LLM generation limit reached. Try again tomorrow.")

        extra = {"response_format": {"type": "json_object"}} if json_mode else {}
        try:
            chat_response = self.client.chat.complete(
                model=self.model, messages=[{"role": "user", "content": prompt}], **extra
            )
            # TODO: return limit to frontend?
            new_count = increment_llm_call_counter(tenant_schema)  # noqa
            logger.info(f"user {tenant_schema} new LLM rate: {new_count}")
            return chat_response.choices[0].message.content

        except Exception as e:
            # Handle any errors that occur during the API call
            print(f"An error occurred with Mistral: {e}")
            return str(e)

    def parse(self, prompt: str, response_format, tenant_schema: str | None = None):
        """Returns an instance of the given Pydantic model, filled in by the LLM."""
        if tenant_schema is not None:
            allowed, _remaining = check_llm_rate_limit(tenant_schema)
            if not allowed:
                raise Throttled(detail="Daily LLM generation limit reached. Try again tomorrow.")

        try:
            parsed = self._parse_with(self.model, prompt, response_format)
        except (json.JSONDecodeError, ValidationError) as e:
            # Small models occasionally degenerate mid-output under constrained decoding
            # (e.g. ministral emitting endless tabs, finish_reason="error"), producing
            # truncated JSON. This is deterministic per prompt, so retry on a stronger model.
            if not self.fallback_model or self.fallback_model == self.model:
                raise
            logger.warning(
                "Structured output from %s was invalid (%s); retrying with %s",
                self.model,
                e,
                self.fallback_model,
            )
            parsed = self._parse_with(self.fallback_model, prompt, response_format)

        if tenant_schema is not None:
            increment_llm_call_counter(tenant_schema)
        return parsed

    def _parse_with(self, model: str, prompt: str, response_format):
        response = self.client.chat.parse(
            response_format=response_format,
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return response.choices[0].message.parsed

    def search(self, query: str) -> ConversationResponse:
        response: ConversationResponse = self.client.beta.conversations.start(
            agent_id=self.search_agent_id, inputs=query
        )
        return response
