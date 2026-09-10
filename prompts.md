# Prompt Log — Flashcard Quizzer

Documents the prompts used to generate and refine the Flashcard Quizzer
using an AI coding assistant (Claude).

---

## Prompt 1 — Project Setup

**Prompt:**
> Create a Python project called `flashcard-quizzer` with a virtual environment.
> Set up this file structure: `main.py`, `models.py`, `data_loader.py`,
> `strategies.py`, `quiz_engine.py`, `ui.py`, `data/glossary.json`,
> `requirements.txt`, `prompts.md`, `README.md`, and `tests/` with
> `conftest.py` and `test_all.py`. Install `pytest`, `pytest-cov`,
> `black`, and `mypy`.

**Result:** Project scaffold created with venv and all files in place.

**Review note:** Confirmed directory structure matches spec before proceeding.

---

## Prompt 2 — Data Model

**Prompt:**
> In `models.py`, create a `Flashcard` dataclass with fields:
> `front: str`, `back: str`, `times_wrong: int = 0`.
> Add `mark_wrong()` that increments `times_wrong` and `reset()` that sets it to 0.
> Add `__post_init__` validation raising `ValueError` if front or back is empty
> or whitespace only. Full type hints required.

**Result:** `models.py` with Flashcard dataclass, validation, and helper methods.

**Review note:** Verified `__post_init__` correctly catches empty and whitespace strings.

---

## Prompt 3 — Data Loader

**Prompt:**
> Create `data_loader.py` with `load_flashcards(filepath: str) -> List[Flashcard]`.
> Handle: file not found, JSON decode errors (show line/column), non-list JSON,
> empty list, items missing 'front' or 'back', non-dict items.
> All errors must call `sys.exit(1)` with a human-readable message — no stack traces.

**Result:** `data_loader.py` with 6 distinct error paths.

**Review note:** Tested all error paths manually. No raw exceptions reach the user.

---

## Prompt 4 — Strategy Pattern

**Prompt:**
> Create `strategies.py` implementing the Strategy Pattern for quiz modes.
> Define abstract base class `QuizStrategy` with abstract method
> `select_cards(cards: List[Flashcard]) -> List[Flashcard]`.
> Implement: `SequentialStrategy` (original order), `RandomStrategy` (shuffled copy),
> `AdaptiveStrategy` (wrong cards first sorted by times_wrong desc, then unseen shuffled).
> Add a `STRATEGIES` dict mapping string names to classes for CLI lookup.

**Result:** `strategies.py` with all three strategies and STRATEGIES registry.

**Review note:** Confirmed AdaptiveStrategy does not mutate the original card list.

---

## Prompt 5 — Quiz Engine

**Prompt:**
> Create `quiz_engine.py` with:
> - `SessionResult` dataclass: `total: int`, `correct: int`,
>   `missed_cards: List[Flashcard]`. Add `accuracy` property returning float %.
> - `QuizEngine` class with `__init__(cards, strategy)` and `run() -> SessionResult`.
>   Compare answers case-insensitively. Call `card.mark_wrong()` on misses.
>   Extract `_ask()`, `_correct_feedback()`, `_wrong_feedback()` as private methods.

**Result:** `quiz_engine.py` with clean I/O separation for testability.

**Review note:** Private method extraction was essential — allows patching
`builtins.input` in tests without modifying engine logic.

---

## Prompt 6 — UI Module

**Prompt:**
> Create `ui.py` with: `print_banner() -> None`, `print_summary(result: SessionResult) -> None`
> showing total, correct, accuracy %, and missed terms list (perfect score message if empty),
> `ask_play_again() -> bool` looping on invalid input. Full type hints.

**Result:** `ui.py` with all three functions.

**Review note:** Verified perfect score message triggers correctly when missed_cards is empty.

---

## Prompt 7 — CLI Entry Point with argparse

**Prompt:**
> Create `main.py` as the CLI entry point using argparse.
> Required flags: `--mode` (choices: sequential, random, adaptive) and
> `--file` (path to JSON file). `--help` must display all flags and examples.
> Use the STRATEGIES dict from strategies.py to look up the chosen strategy class.
> Loop: run quiz, show summary, ask play again. Guard with `if __name__ == "__main__"`.

**Result:** `main.py` with argparse, `--help`, `--mode`, `--file` flags.

**Review note:** Verified `python main.py --help` shows all flags without error.
Verified `python main.py --mode sequential --file data/glossary.json` runs correctly.

---

## Prompt 8 — Test Suite

**Prompt:**
> Create `tests/test_all.py` covering all modules with pytest.
> Tests needed: Flashcard (creation, mark_wrong, reset, validation),
> load_flashcards (valid, all error paths), all three strategies,
> SessionResult accuracy, QuizEngine (correct/wrong/case-insensitive/mixed),
> UI functions, and CLI argument parsing (--help, missing args, invalid mode).
> Use fixtures, tmp_path, patch, capsys. Add conftest.py for sys.path.

**Result:** 35+ test cases across all modules.

**Review note:** All tests pass. Coverage exceeds 80%.

---

## Refinements Made

### Refinement 1 — argparse instead of sys.argv
**Issue:** Initial version used raw `sys.argv` parsing.
**Fix:** Replaced with `argparse` to support `--help`, `--mode`, `--file` flags
as required by the project spec.

### Refinement 2 — STRATEGIES registry
**Issue:** `main.py` had hardcoded if/elif for mode selection.
**Fix:** Added `STRATEGIES` dict to `strategies.py` so `main.py` looks up
the strategy by name — cleaner and extensible.

### Refinement 3 — data/ directory
**Issue:** Initial version used a flat `flashcards.json`.
**Fix:** Moved data file to `data/glossary.json` to match project spec command:
`python main.py --mode sequential --file data/glossary.json`.

### Refinement 4 — Quality tools
**Issue:** Initial requirements only included pytest.
**Fix:** Added `black` and `mypy` to `requirements.txt` as required by the spec.
