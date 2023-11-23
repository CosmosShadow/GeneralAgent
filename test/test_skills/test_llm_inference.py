def test_embedding_single():
    from GeneralAgent import skills
    texts = [
        "我爱唱歌",
        "I love singing"
    ]
    embeddings = [skills.embedding_single(text) for text in texts]
    a, b = embeddings[0], embeddings[1]
    assert skills.cos_sim(a, a) >= 0.999
    assert skills.cos_sim(a, b) > 0.8

def test_embedding_batch():
    from GeneralAgent import skills
    texts = [str(i) for i in range(20)]
    embeddings = skills.embedding_batch(texts)
    assert len(embeddings) == 20


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

if __name__ == '__main__':
    # test_llm_inference_break()
    # test_llm_inference()
    # test_embedding_single()
    test_embedding_batch()