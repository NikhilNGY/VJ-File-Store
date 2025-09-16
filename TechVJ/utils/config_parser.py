from os import environ
from typing import Dict, Optional


class TokenParser:
    """
    A class to parse MULTI_TOKEN variables from environment variables.
    """

    def __init__(self, config_file: Optional[str] = None):
        self.tokens: Dict[int, str] = {}
        self.config_file = config_file

    def parse_from_env(self) -> Dict[int, str]:
        """
        Parse all environment variables that start with MULTI_TOKEN and
        return them as a dictionary where keys are incremental integers starting from 1.

        Returns:
            Dict[int, str]: A dictionary of tokens.
        """
        self.tokens = {
            index + 1: value
            for index, (key, value) in enumerate(
                filter(lambda item: item[0].startswith("MULTI_TOKEN"), sorted(environ.items()))
            )
        }
        return self.tokens