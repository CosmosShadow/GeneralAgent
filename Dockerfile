FROM ubuntu:18.04

RUN sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    sed -i 's/security.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list && \
    apt-get update && apt-get install -y \
    libgl1-mesa-glx libglib2.0-dev \
    build-essential \
    cmake \
    wget \
    curl \
    unzip \
    ca-certificates \
    libjpeg-dev \
    libpng-dev \
    libopenblas-dev \
    libatlas-base-dev \
    gdebi-core

RUN apt-get update && apt-get install -y software-properties-common gcc && \
    add-apt-repository -y ppa:deadsnakes/ppa
ARG DEBIAN_FRONTEND=noninteractive

WORKDIR /tmp/

# python3.8
RUN apt-get update &&apt-get install -y python3.8 python3.8-distutils
RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.8 get-pip.py && rm get-pip.py
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.8 10

# ffmpeg
RUN apt install ffmpeg -y

# python3.8 compile env
RUN apt-get update && apt-get install -y python3.8-dev

# copy source
WORKDIR /workspace
RUN chmod -R a+w /workspace
ADD GeneralAgent ./GeneralAgent
ADD webui ./webui
RUN mkdir ./data

# /workspace添加到python环境变量
ENV PYTHONPATH=/workspace:$PYTHONPATH

# install requirements
ADD ./requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

ADD ./start.sh ./start.sh
RUN chmod +x ./start.sh

CMD [ "./start.sh" ]