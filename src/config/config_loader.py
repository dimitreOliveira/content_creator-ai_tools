import json
from typing import Any, Dict, Optional

import yaml

from utils.logger import setup_logger

logger = setup_logger(__name__)


def load_config(config_path: str = "configs.yaml") -> Optional[Dict[str, Any]]:
    """Loads configuration from a YAML file.

    The function attempts to load the configuration from the specified YAML file.

    Args:
        config_path: Path to the configuration file (YAML).

    Returns:
        A dictionary containing the configuration parameters, or None if loading fails.
        Returns an empty dictionary if the file is empty, rather than None.
    """
    try:
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
        logger.info(f"Configs: \n{json.dumps(config, indent=4)}")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file not found at: {config_path}")
        return None
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML config file: {e}")
        return None
