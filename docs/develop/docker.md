# Work with docker

## Build

```bash
# setting
docker buildx create --use

# build base image
docker buildx build --platform linux/amd64,linux/arm64 -f ./Dockerfile_base -t cosmosshadow/general-agent-base:0.0.1 . --push

# build web
cd webui/web && npm run build && cd ../../

# build general-agent with amd64 and arm64
docker buildx build --platform linux/amd64,linux/arm64 -f ./Dockerfile -t cosmosshadow/general-agent:0.0.1 . --push

# build general-agent-local
docker build -f ./Dockerfile -t cosmosshadow/general-agent-local:0.0.1 .
```

## Develop
```bash
# Mac run
docker run \
-p 3000:3000 \
-p 7777:7777 \
--name=agent \
--privileged=true \
-v `pwd`:/workspace \
--rm=true \
-it cosmosshadow/general-agent:0.0.1 /bin/bash

# run server
export $(grep -v '^#' /workspace/.env | sed 's/^export //g' | xargs)
cd /workspace/webui/server/server
uvicorn app:app --host 0.0.0.0 --port 7777

# run web
docker exec -it agent /bin/bash
cd /workspace/webui/web
# develop
npm run start
# or serve
serve -s build
```

## Run

```bash
# Run with .env file
docker run \
-p 3000:3000 \
-p 7777:7777 \
-v `pwd`/.env:/workspace/.env \
-v `pwd`/data:/workspace/data \
--name=agent \
--privileged=true \
-d cosmosshadow/general-agent:0.0.1

# RUN with ENV
docker run \
--platform linux/amd64 \
-p 3000:3000 \
-p 7777:7777 \
-E "OPENAI_API_KEY=xxxx" \
-v `pwd`/data:/workspace/data \
--name=agent \
--privileged=true \
-d cosmosshadow/general-agent:0.0.1

# Stop
docker stop agent && docker rm agent
```