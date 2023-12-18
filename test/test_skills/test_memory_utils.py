import pytest
import asyncio


content = """
Nougat: Neural Optical Understanding for Academic Documents
Lukas Blecher⇤ Guillem Cucurull Thomas Scialom Robert Stojnic Meta AI
Abstract
Scientific knowledge is predominantly stored in books and scientific journals, often in the form of PDFs. However, the PDF format leads to a loss of semantic information, particularly for mathematical expressions. We propose Nougat (Neural Optical Understanding for Academic Documents), a Visual Transformer model that performs an Optical Character Recognition (OCR) task for processing scientific documents into a markup language, and demonstrate the effectiveness of our model on a new dataset of scientific documents. The proposed approach offers a promising solution to enhance the accessibility of scientific knowledge in the digital age, by bridging the gap between human- readable documents and machine-readable text. We release the models and code to accelerate future work on scientific text recognition.
1 Introduction
The majority of scientific knowledge is stored in books or published in scientific journals, most commonly in the Portable Document Format (PDF). Next to HTML, PDFs are the second most prominent data format on the internet, making up 2.4% of common crawl [1]. However, the information stored in these files is very difficult to extract into any other formats. This is especially true for highly specialized documents, such as scientific research papers, where the semantic information of mathematical expressions is lost.
Existing Optical Character Recognition (OCR) engines, such as Tesseract OCR [2], excel at detecting and classifying individual characters and words in an image, but fail to understand the relationship between them due to their line-by-line approach. This means that they treat superscripts and subscripts in the same way as the surrounding text, which is a significant drawback for mathematical expressions. In mathematical notations like fractions, exponents, and matrices, relative positions of characters are crucial.
Converting academic research papers into machine-readable text also enables accessibility and searchability of science as a whole. The information of millions of academic papers can not be fully accessed because they are locked behind an unreadable format. Existing corpora, such as the S2ORC dataset [3], capture the text of 12M2 papers using GROBID [4], but are missing meaningful representations of the mathematical equations.
To this end, we introduce Nougat, a transformer based model that can convert images of document pages to formatted markup text.
The primary contributions in this paper are
• Release of a pre-trained model capable of converting a PDF to a lightweight markup language. We release the code and the model on GitHub3
• We introduce a pipeline to create dataset for pairing PDFs to source code
• Our method is only dependent on the image of a page, allowing access to scanned papers and books
⇤Correspondence to: lblecher@meta.com
2The paper reports 8.1M papers but the authors recently updated the numbers on the GitHub page https://github.com/allenai/s2orc 3 https://github.com/facebookresearch/nougat
"""

background = """
#01 Nougat is a Visual Transformer model that performs Optical Character Recognition (OCR) on scientific documents, converting them into a markup language. It aims to enhance the accessibility and searchability of scientific knowledge by bridging the gap between human-readable documents and machine-readable text. The model has been released along with the code for future work on scientific text recognition. Detail in <<Nougat: Neural Optical Understanding for Academic Documents>>, <<Introduction>>, <<Related Work>>, <<Model>>, <<Data Augmentation>>, <<Datasets>>
#02 The content discusses the process of splitting a document into pages and predicting the page numbers for each paragraph. It also mentions the use of fuzzy matching to find the exact position within a paragraph. The content acknowledges that there may be artifacts and missing elements in the ground truth data. The results and evaluation section mentions the metrics used to evaluate the model's performance. Detail in <<Page Index>>, <<Staircase Fit>>, <<Predictions>>, <<Figure 4: Splitting Paragraphs into Pages>>, <<Bag of Words Matching>>, <<Fuzzy Matching>>
#03 The model presented, Nougat, is an end-to-end trainable encoder-decoder transformer-based model for converting document pages to markup. It relies solely on the rasterized document page and does not rely on OCR or embedded text representations. The model has shown potential for extracting text from digital-born PDFs and converting scanned papers and textbooks. The model's utility is limited by factors such as repetitions and the need for improvements in handling different document styles. The model's generation speed is slower compared to classical approaches but can correctly parse mathematical expressions. Future work includes addressing the tendency for the model to collapse into a repeating loop and improving the handling of inconsistencies across the document. Detail in <<Numbers and Punctuation>>, <<Math and Plain Text Scores>>, <<Results and Format of GROBID>>, <<Comparison of Approaches>>, <<Repetition Detection and Inference>>, <<Limitations and Future Work>>
#04 Training systems for handwritten mathematical expression recognition, generating LaTeX sequences from math formula images using deep neural networks, and pre-training models for document understanding and image recognition. Detail in <<Training Handwritten Mathematical Expression Recognition>>, <<Neural Markup Generation with Visual Attention>>, <<Multi-Scale Attention for Handwritten Mathematical Expression Recognition>>, <<Translating Math Formula Images to LaTeX Sequences>>, <<Handwritten Mathematical Expression Recognition with Bidirectionally Trained Transformer>>, <<Competition on Recognition of Handwritten Mathematical Expressions>>, <<LaTeX OCR>>, <<Attention Is All You Need>>, <<LayoutLM: Pre-training of Text and Layout for Document Image Understanding>>, <<LayoutLMv2: Multi-modal Pre-training for Visually-Rich Document Understanding>>, <<LayoutLMv3: Pre-training for Document AI with Unified Text and Image Masking>>, <<Online publishing via pdf2htmlEX>>, <<DocFormer: End-to-End Transformer for Document Understanding>>, <<Representation Learning for Information Extraction from Form-like Documents>>, <<OCR-free Document Understanding Transformer>>, <<Swin Transformer: Hierarchical Vision Transformer using Shifted Windows>>, <<An Image is Worth 16x16 Words: Transformers for Image Recognition at Scale>>, <<BART: Denoising Sequence-to-Sequence Pre-training for Natural Language Generation, Translation, and Comprehension>>, <<Galactica: A Large Language Model for Science>>, <<Decoupled Weight Decay Regularization>>, <<Best practices for convolutional neural networks applied to visual document analysis>>, <<Albumentations: Fast and Flexible Image Augmentations>>, <<OCR-IDL: OCR Annotations for Industry Document Library Dataset>>, <<PDFFigures 2.0: Mining Figures from Research Papers>>, <<Binary codes capable of correcting deletions, insertions, and reversals>>, <<Distributional Structure>>, <<Beyond neural scaling laws: beating power law scaling via data pruning>>, <<Bleu: a Method for Automatic Evaluation of Machine Translation>>, <<METEOR: An Automatic Metric for MT Evaluation with Improved Correlation with Human Judgments>>, <<The Curious Case of Neural Text Degeneration>>, <<Calculus>>, <<Kinetics and Thermodynamics in High-Temperature Gases>>, <<Hierarchical Neural Story Generation>>
#05 The content discusses various topics including a dataset composition, examples of text generation, derivative rules, pressure calculations, gas mixtures, and molecular Hamiltonian. Detail in <<Annual Meeting>>, <<Cycle-Consistency for Visual Question Answering>>, <<Dataset Composition>>, <<Examples>>, <<Derivative of a Constant>>, <<Molecular Hamiltonian and Anharmonic Coupling Terms>>
#06 jf (t) is a mathematical function. Detail in <<Segment 1>>, <<Segment 2>>
#07 The content discusses various models and their performance in the field of VQA (Visual Question Answering). It also includes information about a proposed cycle-consistent training framework and its impact on model performance. Additionally, there is mention of evaluation metrics and the effect of hierarchical generation on story generation models. Detail in <<Introduction1>>, <<Description of the Method>>, <<Comparison with Other Models>>, <<Evaluation Metrics and Results>>, <<Effect of Hierarchical Generation>>, <<Perplexity and Accuracy Analysis>>
"""


def test_parse_segment_llm_result():
    from GeneralAgent.skills.memory_utils import _parse_segment_llm_result
    string = "<<Nougat: Neural Optical Understanding for Academic Documents>>\n0: 15\n\n<<Abstract>>\n6: 15\n\n<<Introduction>>\n17: 32\n\n<<Primary Contributions>>\n34: 38"
    nodes = _parse_segment_llm_result(string)
    assert nodes['Abstract'] == (6, 15)
    assert len(nodes) == 4

@pytest.mark.asyncio
def test_segment_text():
    from GeneralAgent import skills
    nodes = skills.segment_text(content)
    assert len(nodes) > 0
    assert 'Abstract' in ''.join(nodes.keys())

@pytest.mark.asyncio
def test_summarize_text():
    from GeneralAgent import skills
    summary = skills.summarize_text(content)
    # print(summary)
    assert len(summary) < len(content)

@pytest.mark.asyncio
def test_extract_info():
    from GeneralAgent import skills
    task = "今天天气怎么样?"
    info = skills.extract_info(background, task)
    assert '[Nothing]' == info

    task = "论文有哪贡献?"
    info = skills.extract_info(background, task)
    print(info)

    task = "论文有哪些限制?"
    info = skills.extract_info(background, task)
    print(info)

def test_parse_extract_info():
    content = """
#01
<<Nougat: Neural Optical Understanding for Academic Documents>>

#03
<<Numbers and Punctuation>>
<<Math and Plain Text Scores>>
<<Results and Format of GROBID>>
<<Comparison of Approaches>>
<<Repetition Detection and Inference>>
<<Limitations and Future Work>>
#03 The model's utility is limited by factors such as repetitions and the need for improvements in handling different document styles. The model's generation speed is slower compared to classical approaches but can correctly parse mathematical expressions. Future work includes addressing the tendency for the model to collapse into a repeating loop and improving the handling of inconsistencies across the document. Detail in <<Repetition Detection and Inference>>, <<Limitations and Future Work>>
"""
    from GeneralAgent import skills
    numbers, titles = skills.parse_extract_info(content)
    assert numbers == [1, 3, 3]
    # print(numbers)
    assert titles == ['Nougat: Neural Optical Understanding for Academic Documents', 'Numbers and Punctuation', 'Math and Plain Text Scores', 'Results and Format of GROBID', 'Comparison of Approaches', 'Repetition Detection and Inference', 'Limitations and Future Work', 'Repetition Detection and Inference', 'Limitations and Future Work']


if __name__ == '__main__':
    # test_parse_segment_llm_result()
    # asyncio.run(test_segment_text())
    # asyncio.run(test_summarize_text())
    # asyncio.run(test_extract_info())
    test_parse_extract_info()