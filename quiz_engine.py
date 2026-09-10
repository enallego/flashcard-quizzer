"""Core quiz engine — runs a quiz session using a given strategy."""

from dataclasses import dataclass, field
from typing import List

from models import Flashcard
from strategies import QuizStrategy


@dataclass
class SessionResult:
    """Holds the results of a completed quiz session."""

    total: int
    correct: int
    missed_cards: List[Flashcard] = field(default_factory=list)

    @property
    def accuracy(self) -> float:
        """Return accuracy as a percentage (0.0 to 100.0)."""
        if self.total == 0:
            return 0.0
        return (self.correct / self.total) * 100.0


class QuizEngine:
    """
    Runs a quiz session.

    Accepts a strategy that determines card ordering, then presents each
    card, checks answers, and tracks results.
    """

    def __init__(self, cards: List[Flashcard], strategy: QuizStrategy) -> None:
        self.cards = cards
        self.strategy = strategy

    def run(self) -> SessionResult:
        """
        Execute the quiz session.

        Returns:
            A SessionResult with totals, accuracy, and missed cards.
        """
        ordered = self.strategy.select_cards(self.cards)
        correct_count = 0
        missed: List[Flashcard] = []

        for card in ordered:
            answer = self._ask(card)
            if answer.strip().lower() == card.back.strip().lower():
                correct_count += 1
                self._correct_feedback()
            else:
                card.mark_wrong()
                missed.append(card)
                self._wrong_feedback(card.back)

        return SessionResult(
            total=len(ordered),
            correct=correct_count,
            missed_cards=missed,
        )

    def _ask(self, card: Flashcard) -> str:
        """Display the card front and get user input."""
        print(f"\nQ: {card.front}")
        return input("Your answer: ")

    def _correct_feedback(self) -> None:
        """Print correct feedback."""
        print("✓ Correct!")

    def _wrong_feedback(self, correct_answer: str) -> None:
        """Print incorrect feedback with the correct answer."""
        print(f"✗ Incorrect. The answer is: {correct_answer}")
