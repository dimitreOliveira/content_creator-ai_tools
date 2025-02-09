import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

from google import genai
from google.genai import types

from client.base_client import BaseClient
from utils.logger import setup_logger

logger = setup_logger(__name__)


class BaseGeminiClient(BaseClient):
    """Base class for the Google Gemini API client, providing common functionality."""

    def _build_prompt_content(
        self, prompt: str, file_upload: Optional[Union[types.File, types.Part]] = None
    ) -> list[Union[str, types.Content, types.Part]]:
        """Builds the prompt content list for the Gemini API.
            Handles both AI Studio and Vertex AI formats.

        Args:
            prompt: The text prompt.
            file_upload: The file upload object (optional).
                Can be either types.File (AI Studio) or types.Part (Vertex).

        Returns:
            A list suitable for the `contents` argument of the Gemini API call.
        """
        logger.info("Building prompt content")
        contents: list[Union[str, types.Content, types.Part]] = [prompt]

        if file_upload:
            if isinstance(file_upload, types.File):
                content = types.Content(
                    parts=[
                        types.Part.from_uri(
                            file_uri=file_upload.uri,
                            mime_type=file_upload.mime_type,
                        )
                    ]
                )
                contents.insert(0, content)
            elif isinstance(file_upload, types.Part):
                contents.insert(0, file_upload)
            else:
                raise TypeError("file_upload must be of type types.File or types.Part")

        return contents

    def count_tokens(
        self, prompt: str, file_upload: Optional[Union[types.File, types.Part]] = None
    ) -> int:
        """Counts the number of tokens in a prompt and optional file content,
            using the Gemini API.

        Args:
            prompt: The text prompt.
            file_upload: The file upload object (optional).
                Can be types.File (AI Studio) or types.Part (Vertex).

        Returns:
            The total number of tokens.
        """

        contents = self._build_prompt_content(prompt, file_upload)

        response = self.client.models.count_tokens(
            model=self.configs["model_id"], contents=contents
        )
        logger.info(f"Prompt had {response.total_tokens} tokens")
        return response.total_tokens

    def generate_content(
        self,
        prompt: str,
        file_upload: Optional[Union[types.File, types.Part]] = None,
    ) -> str:
        """Generates content using the Gemini API, with an optional file as context.

        Args:
            prompt: The text prompt.
            file_upload: The file upload object (optional).
                Can be types.File (AI Studio) or types.Part (Vertex).

        Returns:
            The generated text output.
        """

        contents = self._build_prompt_content(prompt, file_upload)

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
        """Uploads a file to the Gemini API (AI Studio).

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
        """Initializes the Vertex AI Gemini client.

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

    def _build_prompt_content(
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
        contents: list[str | types.Part] = [prompt]

        if file_upload:
            contents = [file_upload, prompt]

        return contents

    def _process_file_for_vertex(self, file_path: str) -> types.Part:
        """Process and format files to be sent as part of a Vertex API request.
            Handles various file types.

        Args:
            file_path: The path to the file to upload.

        Returns:
            types.Part: Processed file data as a types.Part object.

        Raises:
            ValueError: If the file is not found or
                if the file extension is not supported.
        """
        logger.info(f"Processing file '{file_path}' for Vertex AI")
        file_extension = file_path.split(".")[-1].lower()

        try:
            with open(file_path, "rb") as f:
                file_content = f.read()
        except FileNotFoundError:
            error_msg = f"File not found: {file_path}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        except Exception as e:
            error_msg = f"Error reading file {file_path}: {e}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        file_type_handlers = {
            "txt": lambda: types.Part.from_text(file_content.decode()),
            "md": lambda: types.Part.from_text(file_content.decode()),
            "pdf": lambda: types.Part.from_bytes(
                file_content, mime_type="application/pdf"
            ),
            "py": lambda: types.Part.from_bytes(
                file_content, mime_type="text/x-python-script"
            ),
        }

        handler = file_type_handlers.get(file_extension)
        if handler:
            return handler()  # Call the appropriate handler function
        else:
            # Improved error message to suggest converting files
            error_msg = (
                f"File extension '{file_extension}' not supported by Vertex AI. "
                f"Current supported extensions: {', '.join(file_type_handlers.keys())}."
                "Consider converting the file to a supported format."
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

    def upload_file(self, file_path: str) -> types.Part:
        """Uploads and processes a file for use with the Vertex AI Gemini API.

        Args:
            file_path: The path to the file to upload.

        Returns:
            The processed file as a types.Part object.
        """
        file_upload = self._process_file_for_vertex(file_path)
        logger.info(f"Uploaded file: {Path(file_path).name}")
        return file_upload
