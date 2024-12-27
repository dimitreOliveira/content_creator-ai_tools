import json
import logging

import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_config(config_path="configs.yaml"):
    """Loads configuration from a YAML file.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        A dictionary containing the configuration parameters.
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
