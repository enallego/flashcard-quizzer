"""
Comprehensive test suite for the Flashcard Quizzer.

Covers: models, data_loader, strategies, quiz_engine, and ui.
"""

import json
from unittest.mock import patch

import pytest

from data_loader import load_flashcards
from models import Flashcard
from quiz_engine import QuizEngine, SessionResult
from strategies import AdaptiveStrategy, RandomStrategy, SequentialStrategy
from ui import ask_play_again, print_banner, print_summary

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def sample_cards():
    return [
        Flashcard(front="CPU", back="Central Processing Unit"),
        Flashcard(front="RAM", back="Random Access Memory"),
        Flashcard(front="SSD", back="Solid State Drive"),
    ]


@pytest.fixture
def json_file(tmp_path):
    """Write a valid JSON flashcard file and return its path."""
    data = [
        {"front": "CPU", "back": "Central Processing Unit"},
        {"front": "RAM", "back": "Random Access Memory"},
    ]
    p = tmp_path / "cards.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    return str(p)


# ── Model Tests ───────────────────────────────────────────────────────────────


class TestFlashcard:
    def test_creation(self):
        card = Flashcard(front="Q", back="A")
        assert card.front == "Q"
        assert card.back == "A"
        assert card.times_wrong == 0

    def test_mark_wrong(self):
        card = Flashcard(front="Q", back="A")
        card.mark_wrong()
        assert card.times_wrong == 1
        card.mark_wrong()
        assert card.times_wrong == 2

    def test_reset(self):
        card = Flashcard(front="Q", back="A")
        card.mark_wrong()
        card.mark_wrong()
        card.reset()
        assert card.times_wrong == 0

    def test_empty_front_raises(self):
        with pytest.raises(ValueError):
            Flashcard(front="", back="A")

    def test_empty_back_raises(self):
        with pytest.raises(ValueError):
            Flashcard(front="Q", back="")

    def test_whitespace_front_raises(self):
        with pytest.raises(ValueError):
            Flashcard(front="   ", back="A")

    def test_whitespace_back_raises(self):
        with pytest.raises(ValueError):
            Flashcard(front="Q", back="   ")


# ── Data Loader Tests ─────────────────────────────────────────────────────────


class TestDataLoader:
    def test_load_valid_file(self, json_file):
        cards = load_flashcards(json_file)
        assert len(cards) == 2
        assert cards[0].front == "CPU"
        assert cards[1].back == "Random Access Memory"

    def test_missing_file_exits(self, tmp_path):
        with pytest.raises(SystemExit):
            load_flashcards(str(tmp_path / "missing.json"))

    def test_malformed_json_exits(self, tmp_path):
        p = tmp_path / "bad.json"
        p.write_text("{not valid json", encoding="utf-8")
        with pytest.raises(SystemExit):
            load_flashcards(str(p))

    def test_non_list_json_exits(self, tmp_path):
        p = tmp_path / "obj.json"
        p.write_text('{"front": "Q", "back": "A"}', encoding="utf-8")
        with pytest.raises(SystemExit):
            load_flashcards(str(p))

    def test_empty_list_exits(self, tmp_path):
        p = tmp_path / "empty.json"
        p.write_text("[]", encoding="utf-8")
        with pytest.raises(SystemExit):
            load_flashcards(str(p))

    def test_missing_back_key_exits(self, tmp_path):
        p = tmp_path / "noback.json"
        p.write_text('[{"front": "Q"}]', encoding="utf-8")
        with pytest.raises(SystemExit):
            load_flashcards(str(p))

    def test_missing_front_key_exits(self, tmp_path):
        p = tmp_path / "nofront.json"
        p.write_text('[{"back": "A"}]', encoding="utf-8")
        with pytest.raises(SystemExit):
            load_flashcards(str(p))

    def test_non_dict_item_exits(self, tmp_path):
        p = tmp_path / "bad_item.json"
        p.write_text('["not a dict"]', encoding="utf-8")
        with pytest.raises(SystemExit):
            load_flashcards(str(p))


# ── Strategy Tests ────────────────────────────────────────────────────────────


class TestSequentialStrategy:
    def test_preserves_order(self, sample_cards):
        result = SequentialStrategy().select_cards(sample_cards)
        assert [c.front for c in result] == ["CPU", "RAM", "SSD"]

    def test_returns_copy(self, sample_cards):
        result = SequentialStrategy().select_cards(sample_cards)
        assert result is not sample_cards


class TestRandomStrategy:
    def test_same_cards_returned(self, sample_cards):
        result = RandomStrategy().select_cards(sample_cards)
        assert len(result) == len(sample_cards)
        assert set(c.front for c in result) == {"CPU", "RAM", "SSD"}

    def test_returns_correct_count(self, sample_cards):
        result = RandomStrategy().select_cards(sample_cards)
        assert len(result) == 3


class TestAdaptiveStrategy:
    def test_wrong_cards_come_first(self, sample_cards):
        sample_cards[2].times_wrong = 3  # SSD — most wrong
        sample_cards[1].times_wrong = 1  # RAM — wrong once
        result = AdaptiveStrategy().select_cards(sample_cards)
        assert result[0].front == "SSD"
        assert result[1].front == "RAM"

    def test_unseen_cards_at_end(self, sample_cards):
        sample_cards[0].times_wrong = 2
        result = AdaptiveStrategy().select_cards(sample_cards)
        fronts = [c.front for c in result]
        assert fronts.index("CPU") < fronts.index("RAM")
        assert fronts.index("CPU") < fronts.index("SSD")

    def test_all_unseen_returns_all(self, sample_cards):
        result = AdaptiveStrategy().select_cards(sample_cards)
        assert len(result) == 3

    def test_does_not_mutate_original(self, sample_cards):
        sample_cards[0].times_wrong = 1
        original_order = [c.front for c in sample_cards]
        AdaptiveStrategy().select_cards(sample_cards)
        assert [c.front for c in sample_cards] == original_order


# ── Quiz Engine Tests ─────────────────────────────────────────────────────────


class TestSessionResult:
    def test_accuracy_perfect(self):
        r = SessionResult(total=5, correct=5)
        assert r.accuracy == 100.0

    def test_accuracy_zero(self):
        r = SessionResult(total=5, correct=0)
        assert r.accuracy == 0.0

    def test_accuracy_partial(self):
        r = SessionResult(total=4, correct=3)
        assert r.accuracy == 75.0

    def test_accuracy_zero_total(self):
        r = SessionResult(total=0, correct=0)
        assert r.accuracy == 0.0


class TestQuizEngine:
    def test_all_correct(self, sample_cards):
        engine = QuizEngine(cards=sample_cards, strategy=SequentialStrategy())
        answers = [c.back for c in sample_cards]
        with patch("builtins.input", side_effect=answers):
            result = engine.run()
        assert result.correct == 3
        assert result.total == 3
        assert result.missed_cards == []

    def test_all_wrong(self, sample_cards):
        engine = QuizEngine(cards=sample_cards, strategy=SequentialStrategy())
        with patch("builtins.input", side_effect=["wrong"] * 3):
            result = engine.run()
        assert result.correct == 0
        assert len(result.missed_cards) == 3

    def test_case_insensitive(self, sample_cards):
        engine = QuizEngine(cards=sample_cards, strategy=SequentialStrategy())
        answers = [c.back.upper() for c in sample_cards]
        with patch("builtins.input", side_effect=answers):
            result = engine.run()
        assert result.correct == 3

    def test_marks_wrong_on_miss(self, sample_cards):
        engine = QuizEngine(cards=[sample_cards[0]], strategy=SequentialStrategy())
        with patch("builtins.input", return_value="wrong"):
            engine.run()
        assert sample_cards[0].times_wrong == 1

    def test_mixed_results(self, sample_cards):
        engine = QuizEngine(cards=sample_cards, strategy=SequentialStrategy())
        answers = [
            sample_cards[0].back,  # correct
            "wrong",  # incorrect
            sample_cards[2].back,  # correct
        ]
        with patch("builtins.input", side_effect=answers):
            result = engine.run()
        assert result.correct == 2
        assert len(result.missed_cards) == 1
        assert result.missed_cards[0].front == "RAM"


# ── UI Tests ──────────────────────────────────────────────────────────────────


class TestUI:
    def test_print_banner(self, capsys):
        print_banner()
        captured = capsys.readouterr()
        assert "Flashcard Quizzer" in captured.out

    def test_print_summary_perfect(self, capsys):
        result = SessionResult(total=5, correct=5)
        print_summary(result)
        captured = capsys.readouterr()
        assert "100.0%" in captured.out
        assert "Perfect score" in captured.out

    def test_print_summary_with_misses(self, capsys):
        card = Flashcard(front="CPU", back="Central Processing Unit")
        card.mark_wrong()
        result = SessionResult(total=3, correct=2, missed_cards=[card])
        print_summary(result)
        captured = capsys.readouterr()
        assert "CPU" in captured.out
        assert "66.7%" in captured.out

    def test_ask_play_again_yes(self):
        with patch("builtins.input", return_value="y"):
            assert ask_play_again() is True

    def test_ask_play_again_no(self):
        with patch("builtins.input", return_value="n"):
            assert ask_play_again() is False

    def test_ask_play_again_invalid_then_yes(self):
        with patch("builtins.input", side_effect=["maybe", "y"]):
            assert ask_play_again() is True


# ── CLI Tests ─────────────────────────────────────────────────────────────────


class TestCLI:
    def test_help_flag(self):
        """Test that --help exits with code 0."""
        with pytest.raises(SystemExit) as exc:
            from main import parse_args

            with patch("sys.argv", ["main.py", "--help"]):
                parse_args()
        assert exc.value.code == 0

    def test_missing_mode_exits(self):
        with pytest.raises(SystemExit):
            from main import parse_args

            with patch("sys.argv", ["main.py", "--file", "data/glossary.json"]):
                parse_args()

    def test_missing_file_exits(self):
        with pytest.raises(SystemExit):
            from main import parse_args

            with patch("sys.argv", ["main.py", "--mode", "sequential"]):
                parse_args()

    def test_invalid_mode_exits(self):
        with pytest.raises(SystemExit):
            from main import parse_args

            with patch(
                "sys.argv",
                ["main.py", "--mode", "invalid", "--file", "data/glossary.json"],
            ):
                parse_args()
