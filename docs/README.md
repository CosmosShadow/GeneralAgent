# 发布

```bash
# 发布pip库
poetry build -f sdist
poetry publish
```

# 测试

```shell
# 新建python环境
python -m venv ga
source ga/bin/activate

# 安装依赖
pip isntall .

# 导出环境变量
export $(grep -v '^#' .env | sed 's/^export //g' | xargs)

# 测试
cd test
pytest -s -v
```