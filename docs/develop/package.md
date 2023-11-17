```bash
# 安装依赖库
pip install twine

# 本地安装
python setup.py install

# 打包 & 上传
python setup.py sdist bdist_wheel
rm -rf ./GeneralAgent.egg-info
rm -rf ./build
twine upload dist/*
rm -rf ./dist
```