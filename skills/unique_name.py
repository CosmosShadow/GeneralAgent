
def unique_name():
    """Generates a unique name, suitable for creating non-deletable files."""
    """生成唯一的名称，可用于新建文件名，且文件不删除"""
    import uuid
    return str(uuid.uuid4()).split('-')[-1]

def unique_tmp_file_name():
    """Generates a unique temporary file name which needs to be deleted afterwards."""
    """"生成唯一的临时文件名称，且文件需要事后删除"""
    import os
    tmp_dir = os.path.abspath(os.path.join(os.getcwd(), 'tmp'))
    # 如果tmp_dir目录不存在，就创建
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    return tmp_dir + unique_name()