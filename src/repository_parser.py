import logging
from typing import Optional, Tuple

from gitingest import ingest

from utils.logger import setup_logger

logger = setup_logger(__name__)


class RepositoryParser:
    """Parses a git repository into text."""

    def parse_repository(
        self,
        repository_path: str,
        max_file_size: float,
        include_patterns: Optional[str] = None,
        exclude_patterns: str = ".*",
    ) -> Tuple[str, str, str]:
        """Parses a git repository into text.

        Args:
            repository_path: Path to the repository.
            max_file_size: Max file size to include in the parsing process (in megabytes).
            include_patterns: File patterns to include in parsing.
            exclude_patterns: File patterns to exclude in parsing.

        Returns:
            A tuple containing a text summary, the directory structure, and the content of each file.
        """
        logger.info(
            f"""Parsing repository
                 Parsing params:
                    Repository path: {repository_path}
                    Max file size: {max_file_size}
                    Include patterns: {include_patterns}
                    Exclude patterns: {exclude_patterns}"""
        )

        summary, tree, content = ingest(
            source=repository_path,
            max_file_size=max_file_size,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
        )

        logger.info("Parse finished")
        logger.info(f"Parse summary\n{summary}")

        return summary, tree, content
