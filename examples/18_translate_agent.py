# 翻译Agent

def split_text(text, max_token=3000, separators='\n'):
    """
    Split the text into paragraphs, each paragraph has less than max_token tokens.
    """
    import re
    from GeneralAgent import skills
    pattern = "[" + re.escape(separators) + "]"
    paragraphs = list(re.split(pattern, text))
    print(len(paragraphs))
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


def translate_text(text, language, worker=1, reflection_mode=False):
    """
    Translates the given text into the specified language, e.g. translate_text('I love china', 'chinese')
    @param text: The text to be translated
    @param language: The target language
    @param worker: The number of threads to use
    @param reflection_mode: Whether to enable reflection mode. If True, the agent will reflect on the translation result and make improvements.
    """
    from GeneralAgent import skills
    from GeneralAgent import Agent
    from concurrent.futures import ThreadPoolExecutor
    segments = skills.split_text(text, 600)

    def _translate(index, content, language):
        role = f"You are an expert linguist, specializing in translation text to {language}."
        rules = [
            "翻译结果不要包含在```里面",
            "表格、代码、数学公式、图片地址、参考文献等不需要翻译，保持原样",
            "只返回翻译和保留的全文，不要任何解释和描述。",
            "确保翻译的准确性、流畅性和风格一致性",
            "使用目标语言的语法、拼写和标点规则",
            "确保术语使用一致并反映源文本领域",
            "如果有文化背景，请考虑文化背景"
        ]
        role += '# rules: ' + '\n\n'.join([f'{i+1}. {rule}' for i, rule in enumerate(rules)])
        agent = Agent(role)
        result = agent.run(f'请将以下内容翻译成{language}:\n\n{content}')
        if reflection_mode:
            reflection_prompt = f"""Give constructive criticism and helpful suggestions to improve the translation. 
            When writing suggestions, pay attention to whether there are ways to improve the translation's 
            (i) accuracy (by correcting errors of addition, mistranslation, omission, or untranslated text),
            (ii) fluency (by applying {language} grammar, spelling and punctuation rules, and ensuring there are no unnecessary repetitions),
            (iii) style (by ensuring the translations reflect the style of the source text and take into account any cultural context),
            (iv) terminology (by ensuring terminology use is consistent and reflects the source text domain; and by only ensuring you use equivalent idioms {language}).
            Write a list of specific, helpful and constructive suggestions for improving the translation.
            Each suggestion should address one specific part of the translation.
            Output only the suggestions and nothing else."""
            agent.run(reflection_prompt)
            result = agent.run(f'根据反思的结果，对上面的翻译结果进行修改，并只输出修改后的翻译结果。')
        return index, result

    with ThreadPoolExecutor(worker) as executor:
        futures = [executor.submit(_translate, index, content, language) for index, content in enumerate(segments)]
        results = [future.result() for future in futures]
        results.sort(key=lambda x: x[0])
        return '\n\n'.join([x[1] for x in results])
    
if __name__ == '__main__':
    result = translate_text('I love china', 'chinese')