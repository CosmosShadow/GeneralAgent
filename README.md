<h1 align="center">GeneralAgent: From LLM to Agent</h1>

<p align='center'>
A simple, general, customizable Agent framework
</p>


## Features

* Self-Control
* Stack Memory
* Function Search and Call

## Architecture

**GeneralAgent**

![Architecture](./docs/images/Architecture_2023.11.15.png)


## Usage

### docker

```bash
# pull docker
docker pull cosmosshadow/general-agent

# make .env
# download .env.example and copy to .env, then configure environment variables in the .env file, such as OPENAI_API_KEY, etc.
wget https://github.com/CosmosShadow/GeneralAgent/blob/main/.env.example
cp .env.example .env
vim .env
# Configure environment variables in the .env file, such as OPENAI_API_KEY, etc.

# run
docker run \
-p 3000:3000 \
-p 7777:7777 \
-v `pwd`/.env:/workspace/.env \
-v `pwd`/data:/workspace/data \
--name=agent \
--privileged=true \
-d cosmosshadow/general-agent

# open web with localhost:3000
```


### Local installation and usage

#### Installation

```bash
pip install GeneralAgent
```

#### Set environment variables

```bash
# download .env.example and copy to .env, then configure environment variables in the .env file, such as OPENAI_API_KEY, etc.
wget https://github.com/CosmosShadow/GeneralAgent/blob/main/.env.example
cp .env.example .env
vim .env

export $(grep -v '^#' .env | sed 's/^export //g' | xargs)
```

#### WebUI

```bash
git clone https://github.com/CosmosShadow/GeneralAgent
cd GeneralAgent
# Preparation
cd webui/web/ && npm install && cd ../../
cd webui/server/server/ts_builder && npm install && cd ../../../../
# Start the server
cd webui/server/server/
uvicorn app:app --host 0.0.0.0 --port 7777
# Start the web service
cd webui/web
npm run start
```



#### Python usage

Please refer to the code for usage

* [examples](examples)
* [webui/server/server/applications](webui/server/server/applications)



## Development

* Build, code development and release in docker environment: [docs/develop/docker.md](docs/develop/docker.md)
* pip library packaging process: [docs/develop/package.md](docs/develop/package.md)
* Unit testing and release (pip & docker) process: [docs/develop/test_publish.md](docs/develop/test_publish.md)

## License

The intended purpose and licensing of GeneralAgent is solely for research use.

The source code is licensed under Apache 2.0.

## Join us

Scan the QR code below with WeChat

<p align="center">
<img src="./docs/images/wechat.jpg" alt="wechat" width=400/>
</p>