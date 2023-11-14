# Work with docker

## Build Docker Image

```bash
cd webui/web && npm run build && cd ../../

# Mac build
docker buildx build \
--platform linux/amd64 \
-t general-agent .

# Other build
docker buildx build \
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

# Second time enter
docker exec -it agent /bin/bash
cd /workspace/GeneralAgent/webui/web
npm run start
```

## Develop with docker
```bash

```