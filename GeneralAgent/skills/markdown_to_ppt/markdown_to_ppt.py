def add_title_slide(presentation, title):
    # from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.enum.text import PP_ALIGN
    # import re
    slide_layout = presentation.slide_layouts[0]  # 选择标题页布局
    slide = presentation.slides.add_slide(slide_layout)
    title_shape = slide.shapes.title
    # title.text = "Presentation Title"
    title_shape.text = title

    # slide_layout = presentation.slide_layouts[5]  # 选择只有标题的幻灯片布局
    # slide = presentation.slides.add_slide(slide_layout)
    # title_placeholder = slide.shapes.title
    # title_placeholder.text = title
    # for paragraph in title_placeholder.text_frame.paragraphs:
    #     paragraph.alignment = PP_ALIGN.CENTER  # 居中对齐标题
    #     for run in paragraph.runs:
    #         run.font.size = Pt(44)  # 设置标题的字体大小


def add_content_slide(presentation, title, content):
    # from pptx import Presentation
    from pptx.util import Inches, Pt
    # import re
    slide_layout = presentation.slide_layouts[1]  # 选择带标题和内容的幻灯片布局
    slide = presentation.slides.add_slide(slide_layout)
    content_placeholder = slide.placeholders[1]
    title_placeholder = slide.shapes.title
    title_placeholder.text = title
    tf = content_placeholder.text_frame
    tf.text = content.strip()
    for paragraph in tf.paragraphs:
        for run in paragraph.runs:
            run.font.size = Pt(18)  # 设置内容的字体大小


def markdown_to_ppt(markdown_file_path):
    """
    convert markdown file to ppt. return ppt file path.
    """
    import re
    from pptx import Presentation
    from pptx.util import Inches, Pt
    from pptx.enum.text import PP_ALIGN

    presentation = Presentation()
    with open(markdown_file_path, 'r', encoding='utf-8') as md_file:
        lines = md_file.readlines()
    
    title = ''
    content = ""
    for line in lines:
        if line.startswith('# '):
            # 如果当前行是标题，先处理之前的内容
            if content:
                add_content_slide(presentation, title, content)
                content = ""
            # 添加标题页
            title = line.replace('#', '').strip()
            add_title_slide(presentation, title)
        else:
            # 累积内容，直到达到300字限制
            if len(content) + len(line) < 300:
                content += line
            else:
                # 当内容超过限制时，添加新的幻灯片
                add_content_slide(presentation, title, content)
                content = line
    
    # 添加最后一段内容的幻灯片（如果有的话）
    if content:
        add_content_slide(presentation, title, content)
            
    # 保存PPT文档
    from GeneralAgent import skills
    ppt_file_path = skills.unique_name() + '.pptx'
    presentation.save(ppt_file_path)

    return ppt_file_path


def test_markdown_to_ppt():
    import os
    markdown_file_path = os.path.join(os.path.dirname(__file__), 'presentation.md')
    ppt_file_path = markdown_to_ppt(markdown_file_path)

if __name__ == '__main__':
    test_markdown_to_ppt()