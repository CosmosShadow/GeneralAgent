<h1 align="center">GeneralAgent: 从LLM到Agent</h1>

<p align="center">
<a href="README.md"><img src="https://img.shields.io/badge/document-English-blue.svg" alt="EN doc"></a>
<a href="README_CN.md"><img src="https://img.shields.io/badge/文档-中文版-blue.svg" alt="CN doc"></a>
<img src="https://img.shields.io/static/v1?label=license&message=MIT&color=white&style=flat" alt="License"/>
</p>

<p align='center'>
一个简单、通用、可定制的Agent框架
</p>



## 特点

* 简单、快速、稳定：**与GPT3.5稳定兼容**。

* GeneralAgent支持**序列化**，包括**Python状态**。

* 内置解释器：Python、AppleScript、Shell、文件、计划、检索嵌入等。

* **动态UI**：Agent可以为用户创建动态UI。

* **Agent Builder**: 使用自然语言创建Agent，并可以马上使用，而无需编码。

* [AthenaAgent](https://github.com/sigworld/AthenaAgent)是GeneralAgent的TypeScript版本。



## 架构

**GeneralAgent**



![架构](./docs/images/Architecture_2023.11.15.png)



**WebUI**

<p align="center">
<img src="./docs/images/webui_2023.11.15.png" alt="WebUI" width=600/>
</p>


## 演示

**Version 0.0.11**

![agent builder](./docs/images/2023_11_27_builder_agent.jpg)

![agent created](./docs/images/2023_11_27_image_creator.jpg)

**版本0.03**


![webui](./docs/images/2023.11.15.jpg)


**版本0.0.2**


https://github.com/CosmosShadow/GeneralAgent/assets/13933465/9d9b4d6b-0c9c-404d-87d8-7f8e03f3772b



## 使用方法

### Docker

```bash

# 拉取Docker镜像
docker pull cosmosshadow/general-agent


# 下载.env.example并拷贝成.env，替换其中的变量，如LLM_SOURCE、OPENAI_API_KEY
wget https://github.com/CosmosShadow/GeneralAgent/blob/main/.env.example
cp .env.example .env
vim .env
# 配置.env文件中的环境变量，比如OPENAI_API_KEY等


# 运行
docker run \
-p 3000:3000 \
-p 7777:7777 \
-v `pwd`/.env:/workspace/.env \
-v `pwd`/data:/workspace/data \
--name=agent \
--privileged=true \
-d cosmosshadow/general-agent

# 在本地浏览器中打开localhost:3000
```



### 本地安装使用

#### 安装

```bash
pip install GeneralAgent
```



#### 设置环境变量

```bash
# 下载.env.example并拷贝成.env，替换其中的变量，如LLM_SOURCE、OPENAI_API_KEY
wget https://github.com/CosmosShadow/GeneralAgent/blob/main/.env.example
cp .env.example .env
vim .env
# 配置.env文件中的环境变量，比如OPENAI_API_KEY等
export $(grep -v '^#' .env | sed 's/^export //g' | xargs)
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

请参考代码

* [examples](examples)

* [webui/server/server/applications](webui/server/server/applications)



## 开发

* docker环境下的build、代码开发、发布: [docs/develop/docker.md](docs/develop/docker.md)
* pip库打包流程: [docs/develop/package.md](docs/develop/package.md)
* 单元测试和发布(pip & docker)流程: [docs/develop/test_publish.md](docs/develop/test_publish.md)



## 其他

* GeneralAgent使用[litellm](https://docs.litellm.ai/docs/)来接入各种平台的大模型。

* 如果接入本地LLM和Embedding，可以参考代码:
[llm_inference.py](https://github.com/CosmosShadow/GeneralAgent/blob/main/GeneralAgent/skills/llm_inference.py)，重写下面三个方法:

```python
from GeneralAgent import skills

def llm_inference(messages, model_type='normal', stream=False, json_schema=None):
    pass
skills.llm_inference = llm_inference

def embedding_single(text) -> [float]:
    pass
skills.embedding_single = embedding_single

def embedding_batch(texts) -> [[float]]:
    pass
skills.embedding_batch = embedding_batch

```


## 加入我们

微信扫码下面二维码

<p align="center">
<img src="./docs/images/wechat.jpg" alt="wechat" width=400/>
</p>

discord即将推出。