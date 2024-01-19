# 发布版本: pip & docker

# pip
poetry build -f sdist
# 配置token: poetry config pypi-token.pypi pypi-token-xxxx
poetry publish

# docker
cd webui/web && npm run build && cd ../../
docker buildx build --platform linux/amd64,linux/arm64 -f ./docker/Dockerfile -t cosmosshadow/general-agent:0.2.0 . --push
docker buildx build --platform linux/amd64,linux/arm64 -f ./docker/Dockerfile -t cosmosshadow/general-agent:latest . --push