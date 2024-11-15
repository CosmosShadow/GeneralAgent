from GeneralAgent import skills


def test_embedding_texts():
    texts = ["我爱唱歌", "I love singing"]
    embeddings = skills.embedding_texts(texts)
    a, b = embeddings[0], embeddings[1]
    assert skills.cos_sim(a, a) >= 0.999
    assert skills.cos_sim(a, b) > 0.7


def test_llm_inference():
    messages = [
        {"role": "system", "content": "you are a helpful assistant"},
        {"role": "user", "content": "1 + 1 = ?"},
    ]
    result = ""
    for x in skills.llm_inference(messages, stream=True):
        if x is None:
            break
        result += x
    assert "2" in result
