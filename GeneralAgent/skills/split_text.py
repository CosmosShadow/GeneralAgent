

def split_text(text, max_token=3000, separators='\n'):
    """
    Split the text into paragraphs, each paragraph has less than max_token tokens.
    """
    import re
    from GeneralAgent import skills
    pattern = "[" + re.escape(separators) + "]"
    paragraphs = list(re.split(pattern, text))
    result = []
    current = ''
    for paragraph in paragraphs:
        if skills.string_token_count(current) + skills.string_token_count(paragraph) > max_token:
            result.append(current)
            current = ''
        current += paragraph + '\n'
    if len(current) > 0:
        result.append(current)
    new_result = []
    for x in result:
        if skills.string_token_count(x) > max_token:
            new_result.extend(split_text(x, max_token=max_token, separators="，。,.;；"))
        else:
            new_result.append(x)
    new_result = [x.strip() for x in new_result if len(x.strip()) > 0]
    return new_result