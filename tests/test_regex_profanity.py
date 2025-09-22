import pytest
from pypolite.profanity import SimpleChecker

@pytest.mark.parametrize(
    "text,profanity_words,expected",
    [
        # Basic exact word match
        ("This is a clean sentence", ["badword", "abuse"], False),
        ("This contains badword here", ["badword", "abuse"], True),

        # Case insensitivity
        ("Case insensitive BADWORD check", ["badword", "abuse"], True),

        # Leet speak variants
        ("This is b@dword!", ["badword"], True),
        ("He typed b4dword in chat", ["badword"], True),

        # Repeated letters
        ("He said baaadword loudly", ["badword"], True),
        ("She wrote fuuuck!", ["fuck"], True),

        # Emoji variants (if demojize is applied)
        ("You are a 😠 person", ["angry"], True),

        # Substring tricky cases
        ("I love badass movies", ["ass"], True),
        ("Classic passphrase here", ["ass"], True),  # should not match as standalone

        # Punctuation boundaries
        ("Sh!t! Happens", ["shit"], True),
        ("What the sh*t?", ["shit"], True),

        # Multiple profane words
        ("You are a dumb and ugly person", ["dumb", "ugly"], True),
        ("This is clean", ["dumb", "ugly"], False),

        ("You are a bi**er", ["bitter"], True),
    ],
)
def test_contains_profanity_words_regex(text, profanity_words, expected):
    simple_checker = SimpleChecker(profanity_words=profanity_words, mode="regex")
    assert simple_checker.contains_profanity(text) == expected