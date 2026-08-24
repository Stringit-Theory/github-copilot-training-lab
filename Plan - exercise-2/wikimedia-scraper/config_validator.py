import yaml
import os
from typing import Dict, Any


class ConfigValidator:
    """Validates and loads configuration from YAML/JSON files."""

    REQUIRED_KEYS = {'keyword'}
    OPTIONAL_KEYS = {
        'offset': 0,
        'batch_size': 5,
        'output_file': None,
        'max_retries': 3,
        'request_timeout': 10
    }

    @staticmethod
    def load_config(config_path: str) -> Dict[str, Any]:
        """
        Load and validate configuration from YAML file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dictionary with validated configuration
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If required keys are missing or invalid values
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        if not isinstance(config, dict):
            raise ValueError("Config file must contain a dictionary")

        # Validate required keys
        missing_keys = ConfigValidator.REQUIRED_KEYS - set(config.keys())
        if missing_keys:
            raise ValueError(f"Missing required config keys: {missing_keys}")

        # Merge with defaults for optional keys
        for key, default_value in ConfigValidator.OPTIONAL_KEYS.items():
            if key not in config:
                config[key] = default_value

        # Validate types and values
        ConfigValidator._validate_types(config)

        return config

    @staticmethod
    def _validate_types(config: Dict[str, Any]) -> None:
        """Validate configuration value types and ranges."""
        if not isinstance(config['keyword'], str) or not config['keyword'].strip():
            raise ValueError("'keyword' must be a non-empty string")

        if not isinstance(config['offset'], int) or config['offset'] < 0:
            raise ValueError("'offset' must be a non-negative integer")

        if config['batch_size'] != 5:
            raise ValueError("'batch_size' must be 5 (fixed)")

        if not isinstance(config['max_retries'], int) or config['max_retries'] < 1:
            raise ValueError("'max_retries' must be a positive integer")

        if not isinstance(config['request_timeout'], (int, float)) or config['request_timeout'] <= 0:
            raise ValueError("'request_timeout' must be a positive number")

        if config['output_file'] is not None and not isinstance(config['output_file'], str):
            raise ValueError("'output_file' must be a string or null")
