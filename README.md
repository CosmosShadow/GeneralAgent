<h1 align="center">GeneralAgent: From LLM to Agent</h1>
<p align="center">
<a href="README.md"><img src="https://img.shields.io/badge/document-English-blue.svg" alt="EN doc"></a>
<!-- <a href="README_CN.md"><img src="https://img.shields.io/badge/文档-中文版-blue.svg" alt="CN doc"></a> -->
<img src="https://img.shields.io/static/v1?label=license&message=MIT&color=white&style=flat" alt="License"/>
</p>
<p align='center'>
A simple, general, customizable Agent framework
</p>


## Features

* Simple、Fast、Stable: **stable with GPT3.5**.
* GeneralAgent support **serialization**, include **python state**.
* Build-in interpreters: Python, AppleScript, Shell, File, Plan, Retrieve Embedding etc.
* **Dynamic UI**: Agent can create dynamic ui to user who can use.
* **WebUI with agent builder**. You can use natural language to create agent without coding.
* [AthenaAgent](https://github.com/sigworld/AthenaAgent) is a TypeScript port of GeneralAgent.



## Architecture

**GeneralAgent**

![Architecture](./docs/images/Architecture_2023.11.15.png)

**WebUI**

<p align="center">
<img src="./docs/images/webui_2023.11.15.png" alt="WebUI" width=600/>
</p>


## Demo

**Version 0.03**

![webui](./docs/images/2023.11.15.jpg)



**Version 0.0.2**



https://github.com/CosmosShadow/GeneralAgent/assets/13933465/9d9b4d6b-0c9c-404d-87d8-7f8e03f3772b



## Usage

### docker

```bash
# pull docker
docker pull cosmosshadow/general-agent

# make .env and replace variables like LLM_SOURCE、OPENAI_API_KEY
cp .env.example .env
vim .env
# 配置.env文件中的环境变量，比如OPENAI_API_KEY等

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



### 本地安装使用

#### 安装

```bash
pip install GeneralAgent
```

#### 设置环境变量

```bash
cp .env.example .env
vim .env
# 配置.env文件中的环境变量，比如OPENAI_API_KEY等
export $(grep -v '^#' .env | sed 's/^export //g' | xargs)
```

#### 命令行工具

```shell
GeneralAgent
# or
GeneralAgent --workspace ./test --new --auto_run
# worksapce: Set workspace directory, default ./general_agent
# new: if workspace exists, create a new workspace, like ./general_agent_2023xxx
# auto_run: if auto_run, the agent will run the code automatically, default no
```

#### WebUI

```bash
git clone https://github.com/CosmosShadow/GeneralAgent
cd GeneralAgent
# 准备工作
cd webui/web/ && npm install && cd ../../
cd webui/server/server/ts_builder && npm install && cd ../../../../
# 启动服务端
cd webui/server/server/
uvicorn app:app --host 0.0.0.0 --port 7777
# 启动web服务
cd webui/web
npm run start
```

#### Python使用

使用请参考代码

* [examples](examples)
* [webui/server/server/applications](webui/server/server/applications)



## 其他

* GeneralAgent使用[litellm](https://docs.litellm.ai/docs/)来接入各种平台的大模型。



## 加入我们

微信扫码下面二维码

<p align="center">
<img src="./docs/images/wechat.jpg" alt="wechat" width=400/>
</p>

discord is comming soon.