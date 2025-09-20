import pytest
from pypolite.profanity import contains_profanity_words


@pytest.mark.parametrize(
    "text,profanity_words,expected",
    [
        ("This is a clean sentence", ["badword", "abuse"], False),
        ("This contains badword here", ["badword", "abuse"], True),
        ("Nothing abusive here", ["badword", "abuse"], False),
        ("Case insensitive BADWORD check", ["badword", "abuse"], True),
    ],
)
def test_contains_profanity_words(text, profanity_words, expected):
    assert contains_profanity_words(text, profanity_words) == expected
