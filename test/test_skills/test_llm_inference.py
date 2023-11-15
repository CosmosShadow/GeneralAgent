def test_embedding_fun():
    from GeneralAgent import skills
    texts = [
        "我爱唱歌",
        "I love singing"
    ]
    embeddings = [skills.embedding_single(text) for text in texts]
    a, b = embeddings[0], embeddings[1]
    assert skills.cos_sim(a, a) >= 0.999
    assert skills.cos_sim(a, b) > 0.8


def test_llm_inference():
    messages = [
        {'role': 'system', 'content': 'you are a helpful assistant'},
        {'role': 'user', 'content': '1 + 1 = ?'},
    ]
    result = ''
    from GeneralAgent import skills
    for x in skills.llm_inference(messages, stream=True):
        if x is None:
            break
        result += x
    assert '2' in result

def test_llm_inference_break():
    messages = [
        {'role': 'system', 'content': 'you are a helpful assistant'},
        {'role': 'user', 'content': 'describle the Chengdu'},
    ]
    result = ''
    from GeneralAgent import skills
    for x in skills.llm_inference(messages, stream=True):
        if x is None:
            break
        # print(x, end='', flush=True)
        result += x
        if len(result) > 10:
            break
    assert len(result) > 10

    result = ''
    from GeneralAgent import skills
    for x in skills.llm_inference(messages, stream=True):
        result += x
        if len(result) > 10:
            break
    assert len(result) > 10