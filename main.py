"""
Flashcard Quizzer — entry point.

Usage:
    python main.py --help
    python main.py --mode sequential --file data/glossary.json
    python main.py --mode random --file data/glossary.json
    python main.py --mode adaptive --file data/glossary.json
"""

import argparse

from data_loader import load_flashcards
from quiz_engine import QuizEngine
from strategies import STRATEGIES
from ui import ask_play_again, print_banner, print_summary


def parse_args() -> argparse.Namespace:
    """Parse and return CLI arguments."""
    parser = argparse.ArgumentParser(
        prog="flashcard-quizzer",
        description="A CLI flashcard quiz application with multiple quiz modes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Quiz Modes:
  sequential  Cards are presented in the order they appear in the file.
  random      Cards are shuffled randomly each session.
  adaptive    Cards you got wrong appear first (ordered by miss count).

Examples:
  python main.py --mode sequential --file data/glossary.json
  python main.py --mode random --file data/glossary.json
  python main.py --mode adaptive --file data/glossary.json
        """,
    )
    parser.add_argument(
        "--mode",
        choices=list(STRATEGIES.keys()),
        required=True,
        help="Quiz mode: sequential, random, or adaptive.",
    )
    parser.add_argument(
        "--file",
        required=True,
        help="Path to the JSON flashcard file (e.g. data/glossary.json).",
    )
    return parser.parse_args()


def main() -> None:
    """Run the Flashcard Quizzer application."""
    args = parse_args()

    cards = load_flashcards(args.file)
    strategy = STRATEGIES[args.mode]()

    print_banner()
    print(f"\nLoaded {len(cards)} flashcard(s) from '{args.file}'.")
    print(f"Mode: {args.mode.capitalize()}\n")

    while True:
        engine = QuizEngine(cards=cards, strategy=strategy)
        result = engine.run()
        print_summary(result)

        if not ask_play_again():
            print("\nGoodbye! Keep studying. 👋")
            break


if __name__ == "__main__":
    main()
