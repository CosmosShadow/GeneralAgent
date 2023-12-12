# 发布版本: pip & docker

# pip
poetry build -f sdist
poetry publish -u lichen -p $PYPI_PASSWORD

# docker
cd webui/web && npm run build && cd ../../
docker buildx build --platform linux/amd64,linux/arm64 -f ./docker/Dockerfile -t cosmosshadow/general-agent:0.1.0 . --push
docker buildx build --platform linux/amd64,linux/arm64 -f ./docker/Dockerfile -t cosmosshadow/general-agent:latest . --push