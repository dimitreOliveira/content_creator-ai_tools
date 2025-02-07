import os
from pathlib import Path
from typing import Any, Dict, Optional

from google import genai
from google.genai import types

from client.base_client import BaseClient
from utils.logger import setup_logger

logger = setup_logger(__name__)


class BaseGeminiClient(BaseClient):
    """Base class for the Google Gemini API client."""

    def build_prompt_content(
        self, prompt: str, file_upload: Optional[types.File | types.Part] = None
    ) -> list:
        """Builds the prompt content to be used by the Gemini API.

        Args:
            prompt: The text prompt.
            file_upload: The file upload object (optional).

        Returns:
            Content list
        """

        logger.info("Building prompt content")
        contents = [prompt]

        if file_upload:
            contents = [
                types.Content(
                    parts=[
                        types.Part.from_uri(
                            file_uri=file_upload.uri,
                            mime_type=file_upload.mime_type,
                        )
                    ]
                )
            ] + contents

        return contents

    def count_tokens(
        self, prompt: str, file_upload: Optional[types.File | types.Part] = None
    ) -> int:
        """Counts the number of tokens in a prompt, including file content.

        Args:
            prompt: The text prompt.
            file_upload: The file upload object (optional).

        Returns:
            The total number of tokens.
        """

        contents = self.build_prompt_content(prompt, file_upload)

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

        contents = self.build_prompt_content(prompt, file_upload)

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


class AIStudioGeminiClient(BaseGeminiClient):
    """Class for the AI Studio Google Gemini API client."""

    def __init__(self, configs: Dict[str, Any]):
        """Initializes the Gemini client.

        Args:
            configs: Configs for the LLM provider.
        """

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
        logger.info(f"Uploaded file: {Path(file_path).name}")
        logger.info(f"Uploaded file URI: {file_upload.uri}")
        return file_upload


class VertexAIGeminiClient(BaseGeminiClient):
    """Class for the Google Gemini API client."""

    def __init__(self, configs: Dict[str, Any], vertex_ai_configs: Dict[str, Any]):
        """Initializes the Gemini client.

        Args:
            configs: Configs for the LLM provider.
            vertex_ai_configs: Configs for Vertex AI.
        """

        self.client = genai.Client(
            vertexai=True,
            project=vertex_ai_configs["project"],
            location=vertex_ai_configs["location"],
        )
        self.configs = configs
        logger.info(f"Gemini client intialized with configs: {self.configs}")

    def build_prompt_content(
        self, prompt: str, file_upload: Optional[types.File | types.Part] = None
    ) -> list:
        """Builds the prompt content to be used by the Gemini API.

        Args:
            prompt: The text prompt.
            file_upload: The file upload object (optional).

        Returns:
            Content list
        """

        logger.info("Building prompt content")
        contents = [prompt]

        if file_upload:
            contents = [file_upload, prompt]

        return contents

    def process_file_for_vertex(self, file_path: str) -> types.Part:
        """Process and format files to be sent as part of a Vertex API request.

        Args:
            file_path: The path to the file to upload.

        Returns:
            types.Part: Processed file.
        """
        logger.info("Processing files for Vertex")

        logger.info(f"Processing file '{file_path}'")
        file_extension = file_path.split(".")[-1]
        file_content = open(file_path, "rb").read()
        if file_extension in ["txt", "md"]:
            file = types.Part.from_text(file_content.decode())
        elif file_extension in ["pdf"]:
            file = types.Part.from_bytes(file_content, mime_type="application/pdf")
        elif file_extension in ["py"]:
            file = types.Part.from_bytes(file_content, mime_type="text/x-python-script")
        else:
            logger.info(
                "File extension not supported by Vertex AI, "
                "currently only supported (.txt, .md, .pdf, .py)."
            )
            raise ValueError(
                "File extension not supported by Vertex AI, "
                "currently only supported (.txt, .md, .pdf, .py)."
            )

        return file

    def upload_file(self, file_path: str) -> types.File:
        """Uploads a file to the Gemini API.

        Args:
            file_path: The path to the file to upload.

        Returns:
            The file upload object from the API.
        """
        file_upload = self.process_file_for_vertex(file_path)
        logger.info(f"Uploaded file: {Path(file_path).name}")
        return file_upload
