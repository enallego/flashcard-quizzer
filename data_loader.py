"""Handles loading and validating flashcard data from JSON files."""

import sys
from pathlib import Path
from typing import List

from models import Flashcard
from utils.file_handler import FileHandler


def load_flashcards(filepath: str) -> List[Flashcard]:
    """
    Load flashcards from a JSON file using FileHandler.

    Args:
        filepath: Path to the JSON file.

    Returns:
        A list of Flashcard objects.

    Raises:
        SystemExit: If the file is missing, malformed, or invalid.
    """
    path = Path(filepath)
    if not path.is_absolute():
        base_dir = Path(__file__).resolve().parent
        candidate = base_dir / filepath
        if candidate.exists():
            path = candidate

    handler = FileHandler()

    if not path.exists():
        print(f"Error: File not found — '{filepath}'")
        print("Please provide a valid path to a JSON flashcard file.")
        sys.exit(1)

    try:
        data = handler.load_data(str(path))
    except RuntimeError as e:
        print(f"Error: Could not load '{filepath}'.")
        print(f"Details: {e}")
        sys.exit(1)

    if not isinstance(data, list):
        print("Error: JSON file must contain a list of flashcard objects.")
        print('Expected format: [{"front": "...", "back": "..."}, ...]')
        sys.exit(1)

    if len(data) == 0:
        print("Error: Flashcard file is empty. Please add at least one card.")
        sys.exit(1)

    flashcards: List[Flashcard] = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            print(f"Error: Item at index {i} is not an object.")
            sys.exit(1)
        if "front" not in item or "back" not in item:
            print(
                f"Error: Item at index {i} is missing"
                " 'front' or 'back' key."
            )
            sys.exit(1)
        try:
            flashcards.append(
                Flashcard(front=str(item["front"]), back=str(item["back"]))
            )
        except ValueError as e:
            print(f"Error: Invalid flashcard at index {i}: {e}")
            sys.exit(1)

    return flashcards
