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
poetry build -f 指定格式 wheel或sdist
# 发布包
poetry publish -u 用户名 -p 密码
```
