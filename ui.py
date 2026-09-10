"""
User interface module.

Handles all terminal output: banners, prompts, and session summary tables.
"""

from quiz_engine import SessionResult


def print_banner() -> None:
    """Print the application banner."""
    print("=" * 50)
    print("        🃏  Flashcard Quizzer  🃏")
    print("=" * 50)


def print_summary(result: SessionResult) -> None:
    """
    Print a formatted session summary table.

    Args:
        result: The SessionResult from a completed quiz session.
    """
    print("\n" + "=" * 50)
    print("              📊 Session Summary")
    print("=" * 50)
    print(f"  Total Questions : {result.total}")
    print(f"  Correct         : {result.correct}")
    print(f"  Accuracy        : {result.accuracy:.1f}%")
    print("-" * 50)

    if result.missed_cards:
        print("  Terms you missed:")
        for card in result.missed_cards:
            times = card.times_wrong
            label = f"(missed {times}x)" if times > 1 else ""
            print(f"    • {card.front:<30} → {card.back}  {label}")
    else:
        print("  🎉 Perfect score! No missed terms.")

    print("=" * 50)


def ask_play_again() -> bool:
    """
    Prompt the user to play again.

    Returns:
        True if the user wants another round, False otherwise.
    """
    while True:
        choice = input("\nPlay again? (y/n): ").strip().lower()
        if choice in ("y", "yes"):
            return True
        if choice in ("n", "no"):
            return False
        print("Please enter y or n.")
