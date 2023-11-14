# Work with docker

## Build Base Docker

```bash
# Mac build
docker buildx build \
--platform linux/amd64 \
-f ./Dockerfile_base \
-t general-agent-base .

# Other build
docker build \
-f ./Dockerfile_base \
-t general-agent-base .
```

## Build Docker Image

```bash
# build web
cd webui/web && npm run build && cd ../../

# Mac build
docker buildx build \
--platform linux/amd64 \
-f ./Dockerfile \
-t general-agent .

# Other build
docker build \
-f ./Dockerfile \
-t general-agent .
```

## Develop
```bash
# Mac run
docker run \
--platform linux/amd64 \
-p 3000:3000 \
-p 7777:7777 \
--name=agent \
--privileged=true \
-v `pwd`:/workspace \
--rm=true \
-it general-agent /bin/bash

# Other run
docker run \
-p 3000:3000 \
-p 7777:7777 \
--name=agent \
--privileged=true \
-v `pwd`:/workspace \
--rm=true \
-it general-agent /bin/bash

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

## Develop with docker
```bash

```