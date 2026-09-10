"""
Quiz mode strategies using the Strategy Pattern.

Each strategy defines a different algorithm for ordering flashcards.
New modes can be added by implementing QuizStrategy.
"""

import random
from abc import ABC, abstractmethod
from typing import Dict, List, Type

from models import Flashcard


class QuizStrategy(ABC):
    """Abstract base class for quiz ordering strategies."""

    @abstractmethod
    def select_cards(self, cards: List[Flashcard]) -> List[Flashcard]:
        """
        Return an ordered list of cards to quiz the user on.

        Args:
            cards: The full deck of flashcards.

        Returns:
            An ordered list of flashcards for this quiz session.
        """


class SequentialStrategy(QuizStrategy):
    """Present cards in the original file order (1 to N)."""

    def select_cards(self, cards: List[Flashcard]) -> List[Flashcard]:
        return list(cards)


class RandomStrategy(QuizStrategy):
    """Present cards in a randomly shuffled order."""

    def select_cards(self, cards: List[Flashcard]) -> List[Flashcard]:
        shuffled = list(cards)
        random.shuffle(shuffled)
        return shuffled


class AdaptiveStrategy(QuizStrategy):
    """
    Prioritize cards the user has previously got wrong.

    Cards with more wrong answers appear earlier.
    Cards never answered incorrectly appear at the end.
    """

    def select_cards(self, cards: List[Flashcard]) -> List[Flashcard]:
        wrong = [c for c in cards if c.times_wrong > 0]
        unseen = [c for c in cards if c.times_wrong == 0]

        wrong.sort(key=lambda c: c.times_wrong, reverse=True)
        random.shuffle(unseen)

        return wrong + unseen


STRATEGIES: Dict[str, Type[QuizStrategy]] = {
    "sequential": SequentialStrategy,
    "random": RandomStrategy,
    "adaptive": AdaptiveStrategy,
}
