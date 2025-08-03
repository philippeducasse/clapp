from dotenv import load_dotenv
from mistralai import Mistral
import os
from typing import Dict, Any, Union


def call_mistral_api(model: str, prompt: str) -> Union[str, Dict[str, Any]]:
    load_dotenv(".env")
    api_key: str = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY environment variable not set.")
    client: Mistral = Mistral(api_key=api_key)

    try:
        # Call the Mistral API to get a chat response
        chat_response = client.chat.complete(
            model=model, messages=[{"role": "user", "content": prompt}]
        )
        # Extract and return the content of the response
        return chat_response.choices[0].message.content

    except Exception as e:
        # Handle any errors that occur during the API call
        print(f"An error occurred: {e}")
        return {"error": str(e)}
