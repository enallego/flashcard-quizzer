"""Data models for the Flashcard Quizzer application."""

from dataclasses import dataclass, field


@dataclass
class Flashcard:
    """Represents a single flashcard with a front and back."""

    front: str
    back: str
    times_wrong: int = field(default=0)

    def __post_init__(self) -> None:
        if not self.front or not self.front.strip():
            raise ValueError("Flashcard 'front' must not be empty.")
        if not self.back or not self.back.strip():
            raise ValueError("Flashcard 'back' must not be empty.")

    def mark_wrong(self) -> None:
        """Increment the wrong-answer counter."""
        self.times_wrong += 1

    def reset(self) -> None:
        """Reset the wrong-answer counter."""
        self.times_wrong = 0
