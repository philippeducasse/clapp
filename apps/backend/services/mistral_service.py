from dotenv import load_dotenv
from mistralai import Mistral, ConversationResponse
import os


class MistralClient:
    def __init__(self):
        load_dotenv(".env")
        self.client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))
        self.model = os.getenv("MISTRAL_DEFAULT_MODEL")
        self.search_agent = self.client.beta.agents.create(
            model="mistral-medium-2505",
            description="Agent able to search information regarding circus and street festivals over the web",
            name="Websearch Agent",
            instructions="You have the ability to perform web searches with `web_search` to find up-to-date information.",
            tools=[{"type": "web_search"}],
            completion_args={
                "temperature": 0.3,
                "top_p": 0.95,
            },
        )

    def chat(self, prompt: str) -> str:
        try:
            # Call the Mistral API to get a chat response
            chat_response = self.client.chat.complete(
                model=self.model, messages=[{"role": "user", "content": prompt}]
            )
            # Extract and return the content of the response
            return chat_response.choices[0].message.content

        except Exception as e:
            # Handle any errors that occur during the API call
            print(f"An error occurred: {e}")
            return {"error": str(e)}

    def search(self, query: str):
        response: ConversationResponse = self.client.beta.conversations.start(
            agent_id=self.search_agent.id, inputs=query
        )
        return response
