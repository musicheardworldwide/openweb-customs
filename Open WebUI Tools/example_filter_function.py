"""
title: OpenWebUI Filter Function Template
author: Dr. Wes Caldwell
email: musicheardworldwide@gmail.com
author_url: https://github.com/musicheardworldwide
version: 1.0.0
license: MIT
description: |
  A template for creating filter functions in Open WebUI.
  This function intercepts and modifies user inputs (`inlet`), real-time model stream output (`stream`),
  and final responses (`outlet`).
requirements:
"""
import json
import logging
from typing import Dict, Any, Optional, Callable
from pydantic import BaseModel, Field

# Configure Logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

class Filter(BaseModel):
    """
    A filter function that intercepts and modifies user inputs, real-time model stream output,
    and final responses.
    """
    ENABLE_LOGGING: bool = Field(
        default=True, description="Enable or disable logging for debugging"
    )

    async def inlet(self, message: Dict) -> Dict:
        """
        Intercepts and modifies user inputs before they are processed by the model.
        Args:
            message (Dict): The incoming user message.
        Returns:
            Dict: The modified user message.
        """
        try:
            logger.info(f"Intercepting user input: {message}")
            # Example modification: Add a prefix to the content
            if "content" in message:
                message["content"] = f"[Filtered] {message['content']}"
            return message
        except Exception as e:
            logger.error(f"Error in inlet function: {e}")
            return message

    async def stream(self, chunk: Dict) -> Dict:
        """
        Intercepts and modifies real-time model stream output.
        Args:
            chunk (Dict): A chunk of the model's streaming response.
        Returns:
            Dict: The modified chunk.
        """
        try:
            logger.info(f"Intercepting stream chunk: {chunk}")
            # Example modification: Add a suffix to the content
            if "content" in chunk:
                chunk["content"] = f"{chunk['content']} [Stream Filtered]"
            return chunk
        except Exception as e:
            logger.error(f"Error in stream function: {e}")
            return chunk

    async def outlet(self, response: Dict) -> Dict:
        """
        Intercepts and modifies the final response before it is sent to the user.
        Args:
            response (Dict): The final model response.
        Returns:
            Dict: The modified final response.
        """
        try:
            logger.info(f"Intercepting final response: {response}")
            # Example modification: Add a footer to the content
            if "content" in response:
                response["content"] = f"{response['content']}\n[Filtered Response]"
            return response
        except Exception as e:
            logger.error(f"Error in outlet function: {e}")
            return response

# Example Usage
if __name__ == "__main__":
    filter_function = Filter()

    async def test_filter():
        # Test inlet function
        user_message = {"role": "user", "content": "Hello, world!"}
        modified_message = await filter_function.inlet(user_message)
        print(f"Modified User Message: {json.dumps(modified_message, indent=2)}")

        # Test stream function
        stream_chunk = {"content": "This is a stream chunk."}
        modified_chunk = await filter_function.stream(stream_chunk)
        print(f"Modified Stream Chunk: {json.dumps(modified_chunk, indent=2)}")

        # Test outlet function
        final_response = {"role": "assistant", "content": "Hello from the assistant!"}
        modified_response = await filter_function.outlet(final_response)
        print(f"Modified Final Response: {json.dumps(modified_response, indent=2)}")

    import asyncio
    asyncio.run(test_filter())
