import os
from typing import Any, Dict, Optional

from google import genai
from google.genai import types

from client.base_client import BaseClient
from utils.logger import setup_logger

logger = setup_logger(__name__)


class GeminiClient(BaseClient):
    """Class for the Google Gemini API client."""

    def __init__(self, configs: Dict[str, Any], api_key: Optional[str] = None):
        """Initializes the Gemini client.

        Args:
            api_key: The API key for Gemini API (optional).
                If not provided, it will look for GEMINI_API_KEY env variable
        """
        if not api_key:
            api_key = os.environ.get("GEMINI_API_KEY")
            if not api_key:
                raise ValueError(
                    "No Gemini API key provided and GEMINI_API_KEY env var not set."
                )
        self.client = genai.Client(api_key=api_key)
        self.configs = configs
        logger.info(f"Gemini client intialized with configs: {self.configs}")

    def upload_file(self, file_path: str) -> types.File:
        """Uploads a file to the Gemini API.

        Args:
            file_path: The path to the file to upload.

        Returns:
            The file upload object from the API.
        """
        file_upload = self.client.files.upload(path=file_path)
        logger.info(f"Uploaded file: {file_upload.uri}")
        return file_upload

    def count_tokens(
        self, prompt: str, file_upload: Optional[types.File] = None
    ) -> int:
        """Counts the number of tokens in a prompt, including file content.

        Args:
            prompt: The text prompt.
            file_upload: The file upload object (optional).

        Returns:
            The total number of tokens.
        """

        contents = [prompt]

        if file_upload:
            contents = [
                types.Content(
                    parts=[
                        types.Part.from_uri(
                            file_uri=file_upload.uri, mime_type=file_upload.mime_type
                        )
                    ]
                )
            ] + contents

        response = self.client.models.count_tokens(
            model=self.configs["model_id"], contents=contents
        )
        logger.info(f"Prompt had {response.total_tokens} tokens")
        return response.total_tokens

    def generate_content(
        self,
        prompt: str,
        file_upload: Optional[types.File] = None,
    ) -> str:
        """Generates content using the Gemini API, with an optional file as context.

        Args:
            prompt: The text prompt.
            file_upload: The file upload object (optional).

        Returns:
            The generated text output.
        """

        contents = [prompt]

        if file_upload:
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_uri(
                            file_uri=file_upload.uri, mime_type=file_upload.mime_type
                        )
                    ],
                )
            ] + contents

        response = self.client.models.generate_content(
            model=self.configs["model_id"],
            config=types.GenerateContentConfig(
                temperature=self.configs["generation_config"]["temperature"],
                top_p=self.configs["generation_config"]["top_p"],
                top_k=self.configs["generation_config"]["top_k"],
                max_output_tokens=self.configs["generation_config"][
                    "max_output_tokens"
                ],
            ),
            contents=contents,
        )
        logger.info(f"Text prompt:\n{prompt}")
        logger.info("Content generated")
        return response.text
