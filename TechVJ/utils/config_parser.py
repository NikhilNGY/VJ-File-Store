import os
import json
from typing import Dict, Optional, Union, AsyncIterable
from dotenv import load_dotenv
import yaml  # PyYAML library


class TokenParser:
    """
    Parses multiple bot tokens automatically from environment variables, .env files, JSON, or YAML configs.

    Attributes:
        tokens (Dict[int, str]): Dictionary storing parsed tokens.
    """

    def __init__(self, config_file: Optional[str] = None) -> None:
        self.tokens: Dict[int, str] = {}
        self.config_file = config_file
        if config_file and config_file.endswith(".env"):
            load_dotenv(config_file)  # Load .env if provided

    def parse_from_env(self) -> Dict[int, str]:
        """Parse tokens from environment variables starting with 'MULTI_TOKEN'."""
        self.tokens = {
            idx + 1: token
            for idx, (key, token) in enumerate(
                sorted(filter(lambda item: item[0].startswith("MULTI_TOKEN"), os.environ.items()))
            )
        }
        return self.tokens

    def parse_from_json(self, json_file: str) -> Dict[int, str]:
        """Parse tokens from a JSON config file."""
        with open(json_file, "r") as f:
            data = json.load(f)
        self.tokens = {
            idx + 1: token
            for idx, (key, token) in enumerate(
                sorted(filter(lambda item: item[0].startswith("MULTI_TOKEN"), data.items()))
            )
        }
        return self.tokens

    def parse_from_yaml(self, yaml_file: str) -> Dict[int, str]:
        """Parse tokens from a YAML config file."""
        with open(yaml_file, "r") as f:
            data = yaml.safe_load(f)
        self.tokens = {
            idx + 1: token
            for idx, (key, token) in enumerate(
                sorted(filter(lambda item: item[0].startswith("MULTI_TOKEN"), data.items()))
            )
        }
        return self.tokens

    async def parse_from_async_source(self, async_source: AsyncIterable[Union[tuple, dict]]) -> Dict[int, str]:
        """Parse tokens from an async iterable source."""
        self.tokens = {}
        idx = 1
        async for item in async_source:
            if isinstance(item, dict):
                for key, token in item.items():
                    if key.startswith("MULTI_TOKEN"):
                        self.tokens[idx] = token
                        idx += 1
            elif isinstance(item, tuple):
                key, token = item
                if key.startswith("MULTI_TOKEN"):
                    self.tokens[idx] = token
                    idx += 1
        return self.tokens

    def parse_auto(self) -> Dict[int, str]:
        """
        Automatically detects the source type from the config_file or environment.
        Returns parsed tokens.
        """
        if self.config_file:
            if self.config_file.endswith(".env"):
                return self.parse_from_env()
            elif self.config_file.endswith(".json"):
                return self.parse_from_json(self.config_file)
            elif self.config_file.endswith((".yml", ".yaml")):
                return self.parse_from_yaml(self.config_file)
        # fallback to env variables
        return self.parse_from_env()
