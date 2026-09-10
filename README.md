# 🃏 Flashcard Quizzer

A production-ready CLI flashcard application that helps users memorize terms
through interactive quiz sessions with multiple modes.

---

## Features

- **Three quiz modes** using the Strategy Pattern:
  - **Sequential** — cards in original file order
  - **Random** — shuffled deck each session
  - **Adaptive** — prioritises cards you've previously got wrong
- **Graceful error handling** — helpful messages for missing or malformed JSON
- **Session summary** — accuracy percentage and list of missed terms
- **Type-safe** — full Python type hints throughout
- **Modular architecture** — separated concerns across multiple modules

---

## Project Structure

```
flashcard-quizzer/
├── main.py            # CLI entry point (argparse)
├── models.py          # Flashcard data model
├── data_loader.py     # JSON loading and validation
├── strategies.py      # Quiz mode strategies (Strategy Pattern)
├── quiz_engine.py     # Core quiz loop and session results
├── ui.py              # Terminal UI — banners, prompts, summaries
├── requirements.txt   # Dependencies
├── prompts.md         # AI prompt log
├── data/
│   └── glossary.json  # Sample flashcard deck
└── tests/
    ├── conftest.py    # Pytest path configuration
    └── test_all.py    # Full test suite (35+ tests)
```

---

## Installation

```bash
# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

Python 3.10 or higher is required.

---

## Running the App

```bash
# Show help and all available flags
python main.py --help

# Sequential mode
python main.py --mode sequential --file data/glossary.json

# Random mode
python main.py --mode random --file data/glossary.json

# Adaptive mode (prioritises previously missed cards)
python main.py --mode adaptive --file data/glossary.json
```

---

## Flashcard File Format

The JSON file must be a list of objects with `front` and `back` keys:

```json
[
  {"front": "CPU", "back": "Central Processing Unit"},
  {"front": "RAM", "back": "Random Access Memory"}
]
```

---

## Running the Tests

```bash
# Run all tests
pytest tests/

# Run with coverage report
pytest tests/ --cov=. --cov-report=term-missing

# Run with verbose output
pytest tests/ -v
```

## Code Quality

```bash
# Format code
black .

# Type checking
mypy .
```

---

## Quiz Modes

| Mode       | Description                                              |
|------------|----------------------------------------------------------|
| Sequential | Cards in the order they appear in the file               |
| Random     | Cards shuffled randomly each session                     |
| Adaptive   | Cards you got wrong appear first, ordered by miss count  |

---

## Architecture

The **Strategy Pattern** is used for quiz modes. Each mode implements the
`QuizStrategy` abstract base class. New modes can be added without modifying
existing code.

```
QuizStrategy (ABC)
├── SequentialStrategy
├── RandomStrategy
└── AdaptiveStrategy
```
