# utils/profanity.py

def contains_profanity_words(text: str, profanity_words: list[str]) -> bool:
    """
    Check if the given text contains any profanity word.
    Case-insensitive search.
    """
    return any(word.lower() in text.lower() for word in profanity_words)
