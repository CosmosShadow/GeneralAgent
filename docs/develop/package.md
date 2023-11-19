# 初始化环境(新)
```bash
# 创建环境
conda create -n GeneralAgent python=3.8
# 激活环境
conda activate GeneralAgent
# 安装poetry
pip install poetry
# 安装依赖
poetry install
# 添加新依赖
poetry add 依赖包
# 打包
poetry build 
# 发布包
poetry publish
```


# 安装开发环境(旧)

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