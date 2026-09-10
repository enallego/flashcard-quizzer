# AI-Assisted Development Project Report

**Student Name:** [Your Name]
**Project Title:** Flashcard Quizzer — CLI Study Tool
**Date:** September 10, 2026

---

## Executive Summary

The Flashcard Quizzer is a production-ready command-line application that helps users
memorize terms and definitions through interactive quiz sessions. The application loads
flashcard data from JSON files and supports three distinct quiz modes: Sequential, Random,
and Adaptive. The Adaptive mode is the standout feature — it tracks which cards the user
answers incorrectly and prioritizes those cards in subsequent sessions, making study time
more efficient.

The application was built by extending the starter code provided in the project repository,
specifically integrating with the existing `FileHandler` utility for JSON data management and
building on the `TaskManager` pattern for the quiz engine's session tracking. AI assistance
was used throughout every phase of development, from initial design to test generation and
code quality enforcement.

AI collaboration was central to the development workflow. Rather than writing code manually,
I acted as an architect — defining requirements, reviewing AI-generated code against a
checklist, identifying problems, and directing the AI to fix them. This process surfaced
several important lessons about AI limitations, particularly around type annotations, import
management, and test reliability.

---

## Project Overview

### Problem Statement

New team members and students often struggle to memorize technical acronyms, terminology,
and concepts. Existing flashcard tools are either web-based (requiring internet access) or
overly complex. There is a clear need for a lightweight, terminal-based tool that can be
run anywhere Python is installed, loads data from a simple JSON file, and intelligently
adapts to what the user finds difficult.

### Solution Approach

The application was designed with a modular architecture, separating concerns across six
distinct modules:

- **`models.py`** — The `Flashcard` dataclass with validation and wrong-answer tracking
- **`data_loader.py`** — JSON loading using the starter's `FileHandler` with graceful error handling
- **`strategies.py`** — Three quiz mode strategies using the Strategy Pattern
- **`quiz_engine.py`** — The core quiz loop and session result tracking
- **`ui.py`** — All terminal output: banners, prompts, and summary tables
- **`main.py`** — CLI entry point using argparse

The key architectural decision was to use the **Strategy Pattern** for quiz modes. This
was directly referenced in the provided `design_patterns.md` guide and serves a genuine
purpose: each mode (Sequential, Random, Adaptive) is a different algorithm for the same
task (selecting the next card). The pattern makes adding new modes — such as Spaced
Repetition — trivial without modifying existing code.

### Final Features

- ✅ Load flashcards from any JSON file via `--file` flag
- ✅ Sequential quiz mode — cards in file order
- ✅ Random quiz mode — shuffled deck each session
- ✅ Adaptive quiz mode — missed cards prioritized by wrong-answer count
- ✅ Case-insensitive answer comparison
- ✅ Immediate correct/incorrect feedback
- ✅ Session summary with accuracy percentage and missed terms list
- ✅ Play-again loop preserving adaptive state across sessions
- ✅ Graceful error handling for all invalid inputs
- ✅ `--help` flag showing all available options and examples

---

## AI Collaboration Experience

### AI Tools Used

- ✅ Claude (primary tool throughout development)

### Collaboration Workflow

My workflow followed a consistent pattern across all development phases:

1. **Decompose first** — Before prompting, I broke each requirement into a single,
   focused task. For example, instead of "build the quiz engine," I asked for the
   `SessionResult` dataclass first, then the `QuizEngine` class separately.

2. **Specify constraints explicitly** — Every prompt included type hint requirements,
   error handling expectations, and which existing modules to import from.

3. **Review against the checklist** — After each AI response, I checked the code against
   the `ai_guidance/code_review_checklist.md` before accepting it.

4. **Run quality tools immediately** — After integrating AI code, I ran `black`, `isort`,
   `flake8`, and `mypy` before moving to the next task. This caught problems early.

5. **Document issues in ai_edit_log.md** — Every modification, rejection, or fix was
   recorded with reasoning.

### Most Valuable AI Interactions

#### Example 1: Strategy Pattern Implementation

**Context:** I needed three quiz mode algorithms that could be swapped at runtime.

**AI Prompt:** Asked Claude to implement the Strategy Pattern with an abstract base class
and three concrete strategies, including the Adaptive mode with wrong-card prioritization.

**AI Response:** Generated correct class structure but AdaptiveStrategy mutated the input
list using `cards.sort()` in place.

**My Changes:** Replaced with separate `wrong` and `unseen` lists, leaving the original
deck unchanged.

**Outcome:** Immutable strategy implementations that work correctly across multiple
play-again sessions.

#### Example 2: Test Suite — Fixing Flaky Tests

**Context:** AI generated a test for AdaptiveStrategy that checked the exact order of
unseen (randomly shuffled) cards.

**AI Prompt:** Asked for comprehensive tests including AdaptiveStrategy ordering behavior.

**AI Response:** Generated `assert result == [card_c, card_b, card_a]` for the unseen
portion — this would fail randomly.

**My Changes:** Changed assertion to only verify wrong cards precede unseen cards,
not their exact sequence.

**Outcome:** Stable test suite with no flaky tests. 42 passing tests, 96% coverage.

#### Example 3: mypy Type Annotation Fix

**Context:** mypy reported an error on `STRATEGIES[args.mode]()` — the dict type was wrong.

**AI Prompt:** Asked Claude to fix the STRATEGIES dict type annotation.

**AI Response:** Suggested `Dict[str, QuizStrategy]` — incorrect (holds classes, not instances).

**My Changes:** Rejected the suggestion and used `Dict[str, Type[QuizStrategy]]` instead.

**Outcome:** mypy passes cleanly. This example showed that AI can struggle with Python's
type-vs-instance distinction.

### Challenges with AI Collaboration

The most consistent challenge was **unused imports**. Every time I asked the AI to refactor
code — such as switching from `sys.argv` to `argparse` — it left the old `import sys`
behind. Running `flake8` after every AI generation became a necessary step.

The second challenge was **import path errors**. When asked to use `FileHandler` from
the starter's `utils/` directory, the AI initially wrote `from utils import FileHandler`
instead of `from utils.file_handler import FileHandler`. This kind of error only surfaces
at runtime, not during code review, making it easy to miss.

---

## Software Engineering Practices

### Code Quality Measures

- ✅ Code formatting with Black
- ✅ Import sorting with isort
- ✅ Linting with flake8 (max-line-length=88)
- ✅ Static type checking with mypy (0 errors)
- ✅ Full type hints on all functions and methods
- ✅ Docstrings on all public functions and classes
- ✅ Graceful error handling with sys.exit(1) and human-readable messages

### Testing Strategy

Tests were written using pytest with the `unittest.mock` library for input simulation.
The test suite covers:

- Unit tests for each module independently
- Edge cases: empty strings, whitespace, zero totals, missing JSON keys
- Integration: QuizEngine with all three strategies
- CLI: argparse flag validation including invalid modes

**Test Coverage: 96%** (well above the 80% requirement)

Tests were written after AI generated the implementation code, reviewing the AI output
to identify gaps. The AI missed the whitespace-only string validation edge case, which
led to adding `test_whitespace_front_raises` and `test_whitespace_back_raises`.

### Design Patterns Used

**Strategy Pattern** (`strategies.py`):

The `QuizStrategy` abstract base class defines the interface. Three concrete strategies
implement it. The `QuizEngine` accepts any `QuizStrategy` instance via its constructor,
making the engine decoupled from any specific mode. This follows the Open/Closed Principle
— new modes can be added without modifying the engine or any existing strategy.

This pattern was not forced — it genuinely solves the problem of having multiple
interchangeable algorithms for card selection. Without it, the engine would need
if/elif branches for each mode, making extension difficult.

### Code Structure and Organization

Separation of concerns was enforced strictly:

- `models.py` has no knowledge of I/O, strategies, or the quiz loop
- `strategies.py` has no knowledge of how answers are checked
- `quiz_engine.py` has no knowledge of CLI arguments or file formats
- `ui.py` has no knowledge of card data or strategies
- `main.py` is the only module that wires everything together

---

## Technical Challenges and Solutions

### Challenge 1: AdaptiveStrategy Mutating Input

**Problem:** AI-generated `AdaptiveStrategy.select_cards()` called `cards.sort()` on the
input list, permanently reordering the deck. This broke the play-again loop.

**Solution:** Created separate `wrong` and `unseen` lists from the input, leaving the
original unchanged.

**AI Involvement:** AI caused the problem. I identified it during code review by
tracing the data flow through the play-again loop.

**Lessons Learned:** Always check whether collection operations mutate their inputs,
especially in methods that receive lists as arguments.

### Challenge 2: mypy Abstract Class Error

**Problem:** mypy reported "Cannot instantiate abstract class QuizStrategy" on
`STRATEGIES[args.mode]()` because the dict was typed as `Dict[str, QuizStrategy]`.

**Solution:** Changed to `Dict[str, Type[QuizStrategy]]` — the dict holds class objects,
not instances.

**AI Involvement:** AI suggested the wrong fix. I rejected it and researched the correct
`Type[]` annotation independently.

**Lessons Learned:** For type annotations involving class objects as values (not instances),
use `Type[ClassName]`. AI is unreliable on this distinction.

### Challenge 3: flake8 Not Reading Config File

**Problem:** `.flake8` config file existed but flake8 kept scanning the `venv/` directory.

**Solution:** Ran flake8 with explicit file arguments:
`flake8 --max-line-length=88 main.py models.py ...` instead of `flake8 .`

**AI Involvement:** None — diagnosed and solved manually.

**Lessons Learned:** Tool configuration files don't always behave as expected in
Windows environments. Explicit arguments are a reliable fallback.

---

## Code Quality Analysis

### Metrics

- **Lines of code:** ~450 (source) + ~220 (tests)
- **Test coverage:** 96%
- **Number of functions/classes:** 18 functions, 7 classes
- **mypy errors:** 0
- **flake8 violations:** 0

### Self-Assessment

- **Code Readability: 5** — Clear module names, descriptive function names, docstrings on all public APIs
- **Code Maintainability: 5** — Strategy Pattern makes adding new modes trivial; modules are fully decoupled
- **Test Quality: 4** — 96% coverage with edge cases; could add property-based testing
- **Documentation: 4** — README, prompts.md, ai_edit_log.md all complete; inline comments could be expanded

---

## Learning Outcomes

### Technical Skills Developed

- Implementing the Strategy Pattern in a real context (not just as an exercise)
- Using `Type[T]` annotations for class-valued dictionaries in mypy
- Configuring and running a full quality tool chain: black, isort, flake8, mypy, pytest-cov
- Writing testable code by extracting I/O into separate private methods

### AI Collaboration Skills

- **Decompose before prompting** — small, focused prompts produce better code than large vague ones
- **Always run linters after AI generation** — AI leaves behind unused imports and style violations
- **Check for mutation** — AI frequently mutates input arguments in collection operations
- **Verify import paths** — AI guesses at module paths; always verify against the actual file structure
- **Don't accept the first type annotation suggestion** — especially for `Type[T]` vs `T`

### Software Engineering Insights

The Strategy Pattern was the most valuable pattern to implement in this context. It taught
me how to design for extension without modification — the quiz engine works with any strategy
I might add in the future, without needing to change a single line of existing code.

Test coverage as a metric is useful but incomplete. 96% coverage did not prevent the
flaky randomized-order test that AI generated — that required reasoning about test design,
not just running coverage reports.

---

## Reflection

### What Worked Well

The workflow of decomposing requirements into focused prompts, running quality tools
immediately, and documenting every change in ai_edit_log.md worked extremely well. By
the end of the project, I had a clear record of every AI mistake and how I fixed it.

The Strategy Pattern decision proved its worth when implementing the play-again loop.
Because the engine accepts any strategy, adding the adaptive feature required zero changes
to the engine — I just passed in a different strategy object.

### What Could Be Improved

I would add spaced repetition as a fourth quiz mode — it's the natural next step for
the Adaptive strategy. I would also add a `--export` flag to save session results to a
JSON file using the starter's FileHandler.

### Future Enhancements

- Spaced repetition mode using the SM-2 algorithm
- Session history export to JSON
- Progress tracking across sessions (persistent wrong-answer counts)
- Support for multiple correct answers per card
- Card difficulty ratings

---

## Conclusion

This project demonstrated that AI-assisted development is most effective when the developer
maintains a clear architectural vision and reviews all generated code systematically. The AI
produced correct structure quickly but consistently made the same categories of mistakes:
unused imports, mutating inputs, incorrect import paths, and flaky tests for randomized behavior.

By treating AI as a fast junior developer rather than a source of ground truth, I caught
these issues early through linting, type checking, and test execution. The result is a
production-quality application with 96% test coverage, zero mypy errors, and clean linting
— an outcome that would have taken significantly longer without AI assistance.

---

## Appendices

### Appendix A: AI Interaction Log

See `docs/ai_edit_log.md` for the complete interaction log with 6 detailed entries
covering: Flashcard model, Strategy Pattern, data loader integration, test suite
generation, CLI argument parsing, and mypy type annotation fixes.

### Appendix B: Code Statistics

```
Name                Stmts   Miss  Cover
---------------------------------------
data_loader.py         39      3    92%
main.py                27     14    48%
models.py              15      0   100%
quiz_engine.py         38      0   100%
strategies.py          23      0   100%
ui.py                  29      0   100%
---------------------------------------
TOTAL                 393     17    96%

Tests: 42 passed in 2.08s
mypy: Success: no issues found in 8 source files
flake8: 0 violations
black: 7 files unchanged
```

### Appendix C: Additional Resources

- Python `abc` module documentation — for implementing the Strategy Pattern correctly
- mypy documentation on `Type[T]` — for understanding class-valued type annotations
- pytest-cov documentation — for configuring coverage reporting
- PEP 8 style guide — enforced via black and flake8
- Provided `ai_guidance/design_patterns.md` — reference for Strategy Pattern selection
- Provided `ai_guidance/code_review_checklist.md` — used after every AI code generation
