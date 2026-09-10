# AI Interaction Log — Flashcard Quizzer

This log documents all meaningful AI interactions during the development of the
Flashcard Quizzer application, including prompts, responses, changes made, and lessons learned.

---

## Interaction 1 — Flashcard Data Model

**Date:** 2026-09-10

**Context:** I needed a core data model for flashcards that would support tracking wrong
answers for the Adaptive quiz mode. The starter code had a TaskManager model I could
reference, but flashcards have different requirements.

**AI Tool Used:** Claude

**Prompt/Request:**
> "Create a Python dataclass called Flashcard in models.py with fields: front: str,
> back: str, and times_wrong: int = 0. Add a mark_wrong() method that increments
> times_wrong and a reset() method that sets it to 0. Add __post_init__ validation
> that raises ValueError if front or back is empty or whitespace only. Use full type hints."

**AI Response:**
Claude generated a clean Flashcard dataclass with __post_init__ validation, mark_wrong(),
and reset() methods. The initial response used `if not self.front:` for validation.

**Changes Made:**
- Changed validation to also catch whitespace-only strings: `if not self.front.strip()`
- Added the whitespace check for the back field as well
- Added a docstring explaining the purpose of each method

**Reasoning:**
The AI's initial check `if not self.front` would pass whitespace strings like "   "
which would create unusable flashcards. Catching this edge case improves robustness.

**Outcome:**
A robust Flashcard dataclass with proper validation that prevents invalid cards
from being created at the data layer.

**Lessons Learned:**
AI generates correct basic validation but misses edge cases like whitespace-only strings.
Always think about boundary conditions the AI may not consider.

---

## Interaction 2 — Strategy Pattern Implementation

**Date:** 2026-09-10

**Context:** The project required different quiz modes (Sequential, Random, Adaptive).
I wanted to use the Strategy Pattern to make modes interchangeable and extensible,
as referenced in the provided design_patterns.md guide.

**AI Tool Used:** Claude

**Prompt/Request:**
> "Create strategies.py implementing the Strategy Pattern for quiz modes. Define an
> abstract base class QuizStrategy with an abstract method select_cards(cards:
> List[Flashcard]) -> List[Flashcard]. Implement three concrete strategies:
> SequentialStrategy (original order), RandomStrategy (shuffled copy), AdaptiveStrategy
> (wrong cards first sorted by times_wrong descending, then unseen cards shuffled).
> Add a STRATEGIES dict mapping string names to classes for CLI lookup."

**AI Response:**
Claude generated all three strategy classes correctly. However, the initial
AdaptiveStrategy implementation sorted the original list in place using
`cards.sort(key=lambda c: c.times_wrong, reverse=True)` which mutated the input.

**Changes Made:**
- Replaced in-place sort with separate wrong/unseen lists:
  ```python
  wrong = [c for c in cards if c.times_wrong > 0]
  unseen = [c for c in cards if c.times_wrong == 0]
  wrong.sort(key=lambda c: c.times_wrong, reverse=True)
  ```
- Added type annotation to STRATEGIES dict: `Dict[str, Type[QuizStrategy]]`

**Reasoning:**
Mutating the original card list would break the play-again loop — cards would
stay in wrong-first order even after the user answered them correctly. Immutability
is critical here. The type annotation was needed to satisfy mypy.

**Outcome:**
Three working strategy classes with proper immutability. mypy passes with no errors.

**Lessons Learned:**
AI often mutates inputs when it shouldn't. Always check whether AI-generated code
modifies its arguments, especially in collection operations.

---

## Interaction 3 — Data Loader with FileHandler Integration

**Date:** 2026-09-10

**Context:** The starter code provided a FileHandler utility in utils/file_handler.py
for JSON file operations. I needed to create a data_loader.py that used this utility
while adding flashcard-specific validation on top.

**AI Tool Used:** Claude

**Prompt/Request:**
> "Create data_loader.py that uses the FileHandler class from utils/file_handler.py
> to load flashcard data. The function load_flashcards(filepath: str) -> List[Flashcard]
> must validate: file exists, valid JSON, is a list, non-empty, each item has front/back
> keys. All errors must call sys.exit(1) with human-readable messages — no stack traces."

**AI Response:**
Claude generated the function but initially imported FileHandler incorrectly as
`from utils import FileHandler` instead of `from utils.file_handler import FileHandler`.
It also used `raise SystemExit` instead of `sys.exit(1)`.

**Changes Made:**
- Fixed import to `from utils.file_handler import FileHandler`
- Changed all `raise SystemExit` to `sys.exit(1)` for consistency
- Added specific line/column information to JSON decode error messages
- Added validation for non-dict items in the list

**Reasoning:**
Correct imports are critical for module resolution. The `sys.exit(1)` convention
is more explicit about the exit code. Line/column info in JSON errors helps users
fix their files faster.

**Outcome:**
A robust loader that gracefully handles all error cases and integrates with the
starter's FileHandler utility.

**Lessons Learned:**
AI frequently gets import paths wrong, especially for nested modules. Always verify
imports match the actual file structure before running the code.

---

## Interaction 4 — Test Suite Generation

**Date:** 2026-09-10

**Context:** I needed comprehensive pytest tests covering all modules with >80% coverage.
The starter had existing tests in tests/ that I needed to extend without breaking.

**AI Tool Used:** Claude

**Prompt/Request:**
> "Create tests/test_all.py with a comprehensive pytest test suite covering all modules.
> Tests needed: Flashcard (creation, mark_wrong, reset, validation), load_flashcards
> (valid, all error paths), all three strategies, SessionResult accuracy, QuizEngine
> (correct/wrong/case-insensitive/mixed), UI functions, and CLI argument parsing.
> Use fixtures, tmp_path, patch, and capsys."

**AI Response:**
Claude generated 35+ test cases. However, two issues were found during review:
1. The AdaptiveStrategy test was checking exact order for unseen cards, which is
   randomised and would fail intermittently.
2. The QuizEngine test was patching `quiz_engine.input` instead of `builtins.input`.

**Changes Made:**
- Fixed AdaptiveStrategy test to only assert wrong cards come before unseen cards,
  not the exact order of unseen cards
- Fixed all input patches to use `builtins.input`
- Added `test_does_not_mutate_original` test for AdaptiveStrategy

**Reasoning:**
Tests that rely on random ordering are flaky and unreliable in CI. The wrong patch
target would cause tests to pass locally but fail in some environments.

**Outcome:**
42 passing tests with 96% coverage. No flaky tests.

**Lessons Learned:**
AI-generated tests often have incorrect mock targets and may test randomised
behaviour in fragile ways. Always run tests multiple times to check for flakiness.

---

## Interaction 5 — CLI Argument Parsing with argparse

**Date:** 2026-09-10

**Context:** The project spec required `--help`, `--mode`, and `--file` flags.
The starter's main.py used raw sys.argv which needed replacing with argparse.

**AI Tool Used:** Claude

**Prompt/Request:**
> "Update main.py to use argparse with --mode (choices: sequential, random, adaptive)
> and --file (path to JSON). --help must show all flags with examples. Use the STRATEGIES
> dict for mode lookup. Remove the unused sys import."

**AI Response:**
Claude generated correct argparse code but left `import sys` in the file even though
sys was no longer used after switching to argparse for argument handling.

**Changes Made:**
- Removed `import sys` (unused — caught by flake8 F401)
- Added epilog with usage examples to the argument parser
- Added `formatter_class=argparse.RawDescriptionHelpFormatter` to preserve formatting

**Reasoning:**
Unused imports are a code smell caught by flake8. The epilog with examples makes
`--help` output much more useful for end users.

**Outcome:**
Clean CLI with `python main.py --help` showing all modes with examples.
flake8 passes with no unused import warnings.

**Lessons Learned:**
AI frequently leaves unused imports behind, especially when refactoring. Always
run linting tools after AI generates code — they catch things code review misses.

---

## Interaction 6 — mypy Type Error Fix

**Date:** 2026-09-10

**Context:** Running mypy produced: "Cannot instantiate abstract class QuizStrategy
with abstract attribute select_cards". The STRATEGIES dict needed proper type annotation.

**AI Tool Used:** Claude

**Prompt/Request:**
> "mypy reports: Cannot instantiate abstract class QuizStrategy with abstract attribute
> select_cards on the line strategy = STRATEGIES[args.mode](). Fix the type annotation
> on the STRATEGIES dict in strategies.py so mypy is satisfied."

**AI Response:**
Claude suggested annotating STRATEGIES as `Dict[str, QuizStrategy]` which was incorrect
— the dict holds classes, not instances.

**Changes Made:**
- Rejected AI suggestion
- Used correct annotation: `Dict[str, Type[QuizStrategy]]`
- Added `from typing import Dict, Type` import

**Reasoning:**
`Dict[str, QuizStrategy]` would mean the dict holds instances. Since we call
`STRATEGIES[args.mode]()` to instantiate, the dict holds classes — hence `Type[QuizStrategy]`.
This is a subtle but important distinction that the AI got wrong.

**Outcome:**
mypy passes with "Success: no issues found in 8 source files."

**Lessons Learned:**
AI can struggle with the distinction between a type and an instance of a type in
Python's type system. For type annotations involving classes-as-values, verify
carefully and don't accept the first suggestion.

---

## Summary of AI Strengths and Weaknesses Observed

### Strengths
- Generates correct boilerplate and structure quickly
- Produces comprehensive test cases covering most scenarios
- Handles standard patterns (dataclasses, argparse, ABC) well
- Good at explaining code and suggesting refactors

### Weaknesses
- Frequently leaves unused imports after refactoring
- Misses edge cases in validation (whitespace-only strings)
- Mutates input arguments when it shouldn't
- Gets import paths wrong for nested modules
- Confused by Python's type vs instance distinction in type annotations
- Generates flaky tests for randomised behaviour
