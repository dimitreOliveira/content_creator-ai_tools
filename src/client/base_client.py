from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from google.genai import types


class BaseClient(ABC):
    """Abstract base class for API clients."""

    def __init__(self, configs: Dict[str, Any]):
        self.configs = configs

    @abstractmethod
    def upload_file(self, file_path: str) -> types.File:
        """Uploads a file to the API.

        Args:
            file_path: The path to the file to upload.

        Returns:
            The file upload object from the API.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def generate_content(
        self, prompt: str, file_upload: Optional[types.File] = None
    ) -> str:
        """Generates content using the API, with an optional file as context.

        Args:
            prompt: The text prompt.
            file_upload: The file upload object (optional).

        Returns:
            The generated text output.
        """
        pass
