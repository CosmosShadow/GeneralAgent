def text_is_english(text):
    """
    Check if a string is an English string.
    """
    import string
    # Remove all whitespace characters
    text = ''.join(text.split())

    # Check if all characters are in the ASCII range
    if all(ord(c) < 128 for c in text):
        # Check if the string contains any non-English characters
        for c in text:
            if c not in string.ascii_letters and c not in string.punctuation and c not in string.digits and c not in string.whitespace:
                return False
        return True
    else:
        return False