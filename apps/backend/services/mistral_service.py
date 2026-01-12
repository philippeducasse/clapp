# mypy: ignore-errors

import logging
import os

from mistralai import ConversationResponse, Mistral
from rest_framework.exceptions import Throttled

from .rate_limit import check_llm_rate_limit, increment_llm_call_counter

logger = logging.getLogger(__name__)


class MistralClient:
    def __init__(self) -> None:
        self.client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
        self.model = os.getenv("MISTRAL_DEFAULT_MODEL")
        self.search_agent = self.client.beta.agents.create(
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

    def chat(self, prompt: str, tenant_schema: str) -> str:
        allowed, _remaining = check_llm_rate_limit(tenant_schema)
        logger.info(f"user {tenant_schema} rate: {allowed}, left: {_remaining}")
        if not allowed:
            raise Throttled(detail="Daily LLM generation limit reached. Try again tomorrow.")

        try:
            chat_response = self.client.chat.complete(
                model=self.model, messages=[{"role": "user", "content": prompt}]
            )
            # TODO: return limit to frontend?
            new_count = increment_llm_call_counter(tenant_schema)  # noqa
            logger.info(f"user {tenant_schema} new LLM rate: {new_count}")
            return chat_response.choices[0].message.content

        except Exception as e:
            # Handle any errors that occur during the API call
            print(f"An error occurred with Mistral: {e}")
            return str(e)

    def search(self, query: str) -> ConversationResponse:
        response: ConversationResponse = self.client.beta.conversations.start(
            agent_id=self.search_agent.id, inputs=query
        )
        return response
