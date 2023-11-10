def test_search_functions():
    from GeneralAgent import skills
    result = skills.search_functions('translate text')
    assert 'skills.translate_text' in result

def test_edit_llm_function():
    from GeneralAgent import skills
    function_name = 'translate_text_test'
    signature = skills.edit_llm_function(function_name, 'Translate text of any length into the specified language.')
    print(signature)
    assert signature.startwith('skills.')
    assert function_name in signature
    skills.delete_function(function_name)


if __name__ == '__main__':
    # test_search_functions()
    test_edit_llm_function()