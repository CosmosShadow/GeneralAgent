
def test_translate_text():
    from GeneralAgent import skills
    result = skills.translate_text('Hello world', '中文')
    print(result)

if __name__ == '__main__':
    test_translate_text()