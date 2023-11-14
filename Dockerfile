FROM general-agent-base:latest

# install requirements
ADD ./requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# copy source
WORKDIR /workspace
RUN chmod -R a+w /workspace
ADD GeneralAgent ./GeneralAgent
ADD webui/server ./webui/server
ADD webui/web/build ./webui/web/build
RUN mkdir ./data

# /workspace添加到python环境变量
ENV PYTHONPATH=/workspace:$PYTHONPATH

ADD ./start.sh ./start.sh
RUN chmod +x ./start.sh

CMD [ "./start.sh" ]