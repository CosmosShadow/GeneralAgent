
def download_file(file_url, save_path):
    """download file to save_path, return True if success, else False"""
    """实现一个下载文件的函数，返回文件路径"""
    import requests
    import logging
    try_count = 3
    while try_count > 0:
        try:
            response = requests.get(file_url)
            with open(save_path, "wb") as f:
                f.write(response.content)
            # print("Success: 文件(%s)已下载至 %s" % (file_url, save_path))
            return True
        except Exception as e:
            # print("Error: 文件下载失败:", e)
            logging.error(e)
            import time
            time.sleep(5)
            try_count -= 1
            continue
    return False


def try_download_file(file_path):
    from GeneralAgent import skills
    """Try to download file if it is a url, else return file_path"""
    if file_path.startswith("http://") or file_path.startswith("https://"):
        remove_parameters = file_path.split('?')[0]
        save_path = skills.unique_name() + '.' + remove_parameters.split('.')[-1]
        success = skills.download_file(file_path, save_path)
        if success:
            return save_path
        else:
            return file_path
    else:
        return file_path

if __name__ == '__main__':
    # download_file('https://ai.tongtianta.site/file-upload/gvsAc4cEm543iaX5x/5.pdf', '1.pdf')
    download_file('https://ai.tongtianta.site/file-upload/27XEb3WgyDru5eFFe/9.pdf', '3.pdf')