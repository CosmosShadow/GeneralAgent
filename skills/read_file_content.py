
def read_pdf_pages(file_path):
    """Read the pdf file and return a list of strings on each page of the pdf"""
    """读取pdf文件，返回pdf每页字符串的列表"""
    if not file_path.endswith('.pdf'):
        return None
    import pypdf
    with open(file_path, "rb") as pdf_file_obj:
        pdf_reader = pypdf.PdfReader(pdf_file_obj)
        return [page.extract_text() for i, page in enumerate(pdf_reader.pages)]
    
def read_word_pages(file_path):
    """Read the word file and return a list of word paragraph strings"""
    """读取word文件，返回word段落字符串的列表"""
    # https://zhuanlan.zhihu.com/p/146363527
    from docx import Document
    # 打开文档
    document = Document(file_path)
    # 读取标题、段落、列表内容
    ps = [ paragraph.text for paragraph in document.paragraphs]
    return ps

def read_file_content(file_path):
    """return content of txt, md, pdf, docx file"""
    # 支持file_path的类型包括txt、md、pdf、docx
    if file_path.endswith('.pdf'):
        return ' '.join(read_pdf_pages(file_path))
    elif file_path.endswith('.docx'):
        return ' '.join(read_word_pages(file_path))
    else:
        # 默认当做文本文件
        with open(file_path, 'r') as f:
            return '\n'.join(f.readlines())
