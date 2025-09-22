import pytest
from pypolite.profanity import SimpleChecker

@pytest.mark.parametrize(
    "text,profanity_words,expected",
    [
        ("This is a clean sentence", ["badword", "abuse"], False),
        ("This contains badword here", ["badword", "abuse"], True),
        ("Nothing abusive here", ["badword", "abuse"], False),
        ("Case insensitive BADWORD check", ["badword", "abuse"], True),
    ],
)
def test_contains_profanity_words_word(text, profanity_words, expected):
    simple_checker = SimpleChecker(profanity_words=profanity_words, mode="word")
    assert simple_checker.contains_profanity(text) == expected