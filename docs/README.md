# 单元测试

```bash
# 单元测试
cd test
pytest -s -v

# 发布pip库
poetry build -f sdist
poetry publish
```