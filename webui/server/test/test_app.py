from base_setting import *
import requests
import pytest
import shutil
import asyncio

def test_bot_list():
    url = HPPT_HOST + '/bot/list'
    r = requests.get(url)
    assert r.status_code == 200
    bot_list = r.json()
    assert len(bot_list) > 0
    ids = [bot['id'] for bot in bot_list]
    assert 'hello' in ids

def test_file():
    path = os.path.join(os.path.dirname(__file__), '../server/applications/hello/hello.jpg')
    url = HPPT_HOST + '/system/file/' + path
    # 获取图片
    r = requests.get(url)
    assert r.status_code == 200
    assert r.headers['Content-Type'] == 'image/jpeg'
    # 获取不存在的图片
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../applications/hello/hello1.jpg'))
    url = HPPT_HOST + '/system/file/' + path
    r = requests.get(url)
    assert r.status_code == 404

# @pytest.mark.asyncio
# async def test_load_application():
#     from GeneralAgent import skills
#     application_module = skills.get_application_module('hello')
#     assert application_module is not None
#     assert hasattr(application_module, 'main')
#     result = ''
#     async def _output(token):
#         nonlocal result
#         result += token
#     await application_module.main(None, None, None, _output)
#     assert 'hello' in result


if __name__ == '__main__':
    # test_bot_list()
    # test_file()
    asyncio.run(test_load_application())