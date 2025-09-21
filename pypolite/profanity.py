def contains_profanity_words(text, profanity_words) -> bool:
    """
    Check if the given text contains any profanity word.
    Case-insensitive search.
    """
    return any(word.lower() in text.lower() for word in profanity_words)
