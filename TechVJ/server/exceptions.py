# TechVJ/server/exceptions.py

class TechVJException(Exception):
    """Base exception for TechVJ server errors."""
    default_message = "An unexpected error occurred"

    def __init__(self, message: str = None):
        super().__init__(message or self.default_message)
        self.message = message or self.default_message

    def __str__(self):
        return self.message


class InvalidHash(TechVJException):
    """Raised when a provided hash is invalid."""
    default_message = "Invalid hash"


class FileNotFound(TechVJException):
    """Raised when a requested file is not found."""
    default_message = "File not found"
