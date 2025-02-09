from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseClient(ABC):
    """Abstract base class for API clients."""

    def __init__(self, configs: Dict[str, Any]):
        """Initializes the BaseClient with configuration settings.

        Args:
            configs: A dictionary of configuration settings.
        """
        self.configs = configs

    @abstractmethod
    def upload_file(self, file_path: str) -> Any:  # type: ignore
        """Uploads a file to the API.
        The return type will be specific to the implementation.

        Args:
            file_path: The path to the file to upload.

        Returns:
            The file upload object from the API, specific to the implementation.
        """
        pass

    @abstractmethod
    def count_tokens(
        self, prompt: str, file_upload: Optional[Any] = None  # type: ignore
    ) -> int:
        """Counts the number of tokens in a prompt, including file content.

        Args:
            prompt: The text prompt.
            file_upload: The file upload object (optional).
                Specific type depends on implementation.

        Returns:
            The total number of tokens.
        """
        pass

    @abstractmethod
    def generate_content(
        self, prompt: str, file_upload: Optional[Any] = None  # type: ignore
    ) -> str:
        """Generates content using the API, with an optional file as context.

        Args:
            prompt: The text prompt.
            file_upload: The file upload object (optional).
                Specific type depends on implementation.

        Returns:
            The generated text output.
        """
        pass
