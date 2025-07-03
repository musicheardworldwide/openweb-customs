"""
title: OpenWebUI Advanced Filter
author: Wes Caldwell
email: musicheardworldwide@gmail.com
author_url: https://github.com/musicheardworldwide
version: 1.0.0
license: MIT
description: A structured Open WebUI filter with advanced text sanitization, JSON enforcement, and error handling.
requirements:
"""
import json
import logging
import traceback
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

# Configure Logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Centralized Error Handling Function
def handle_error(exception: Exception, function_name: str, inputs: dict) -> dict:
    """
    Handles errors and returns a structured response for OpenWebUI.
    Args:
        exception (Exception): The caught exception.
        function_name (str): The name of the function where the error occurred.
        inputs (dict): The original function inputs for debugging.
    Returns:
        dict: A structured error message to pass to OpenWebUI.
    """
    error_message = str(exception)
    stack_trace = traceback.format_exc()
    logger.error(f"Error in {function_name}: {error_message}")
    logger.debug(f"Stack Trace:\n{stack_trace}")
    return {
        "error": True,
        "function": function_name,
        "message": error_message,
        "stack_trace": stack_trace,
        "inputs": inputs,
        "suggestion": "Check input values and ensure the correct filter configurations.",
    }

# Filter Definition
class Filter:
    """
    OpenWebUI Filter for modifying input and output data dynamically.
    """
    class Config(BaseModel):
        ENABLE_TEXT_SANITIZATION: bool = Field(
            default=True, description="Enable text sanitization for user inputs."
        )
        REMOVE_PROFANITY: bool = Field(
            default=True, description="Filter explicit content from AI responses."
        )
        ENFORCE_JSON_OUTPUT: bool = Field(
            default=False, description="Ensure output responses conform to JSON format."
        )

    def __init__(self):
        self.config = self.Config()

    def inlet(self, body: Dict, __user__: Optional[Dict] = None) -> Dict:
        """
        Modifies input data before it reaches the AI model.
        Args:
            body (Dict): The request payload.
            __user__ (Optional[Dict]): User metadata.
        Returns:
            Dict: Modified request payload.
        """
        try:
            logger.info("Filtering input data...")
            messages = body.get("messages", [])
            if messages:
                user_message = messages[-1]["content"]
                # Perform text sanitization
                if self.config.ENABLE_TEXT_SANITIZATION:
                    user_message = self.sanitize_text(user_message)
                body["messages"][-1]["content"] = user_message
            return body
        except Exception as e:
            return handle_error(e, "inlet", body)

    def outlet(self, body: Dict, __user__: Optional[Dict] = None) -> Dict:
        """
        Modifies AI-generated responses before sending them to the user.
        Args:
            body (Dict): The response payload.
            __user__ (Optional[Dict]): User metadata.
        Returns:
            Dict: Modified response payload.
        """
        try:
            logger.info("Filtering output data...")
            for message in body.get("messages", []):
                message_content = message["content"]
                # Remove explicit words if enabled
                if self.config.REMOVE_PROFANITY:
                    message_content = self.remove_profanity(message_content)
                # Enforce JSON format if required
                if self.config.ENFORCE_JSON_OUTPUT:
                    message_content = self.ensure_json_format(message_content)
                message["content"] = message_content
            return body
        except Exception as e:
            return handle_error(e, "outlet", body)

    def sanitize_text(self, text: str) -> str:
        """
        Basic text sanitization function.
        Args:
            text (str): The input text.
        Returns:
            str: Sanitized text.
        """
        text = text.replace("badword", "***")  # Example censorship
        return text

    def remove_profanity(self, text: str) -> str:
        """
        Censors explicit words from responses.
        Args:
            text (str): The output text.
        Returns:
            str: Cleaned text.
        """
        profanity_list = [
            "damn",
            "hell",
            "curseword1",
            "curseword2",
        ]  # Example profanity list
        for word in profanity_list:
            text = text.replace(word, "***")
        return text

    def ensure_json_format(self, text: str) -> str:
        """
        Ensures the output is structured as JSON.
        Args:
            text (str): The output text.
        Returns:
            str: JSON-compliant string.
        """
        return json.dumps({"response": text})

# Example Usage
if __name__ == "__main__":
    filter_obj = Filter()
    # Simulate an OpenWebUI message
    test_input = {
        "messages": [{"role": "user", "content": "Hello! This is a badword test."}]
    }
    # Process Input Filtering
    filtered_input = filter_obj.inlet(test_input)
    print("Filtered Input:", json.dumps(filtered_input, indent=4))
    # Simulate AI-generated output
    test_output = {
        "messages": [{"role": "assistant", "content": "This is a damn great response."}]
    }
    # Process Output Filtering
    filtered_output = filter_obj.outlet(test_output)
    print("Filtered Output:", json.dumps(filtered_output, indent=4))
