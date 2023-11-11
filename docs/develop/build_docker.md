# Build Docker

## Build Docker Image

```bash
cd webui/web && npm run build && cd ../../

docker buildx build \
--platform linux/amd64 \
-t general-agent .
```

## Run docker
```bash
docker run general-agent
```

## Develop with docker
```bash

```