from typing import Protocol


class ImageClient(Protocol):
    name: str

    def generate_background(self, *, prompt: str, width: int, height: int) -> str:
        """Generate or render a clean visual background without text and return local storage path."""
        ...
