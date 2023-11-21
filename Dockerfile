FROM cosmosshadow/general-agent-base:0.0.2

WORKDIR /workspace

# install requirements
ADD ./pyproject.toml ./pyproject.toml
RUN pip install poetry && poetry install

# copy source
RUN chmod -R a+w /workspace
ADD GeneralAgent ./GeneralAgent
ADD webui/server ./webui/server
ADD webui/web/build ./webui/web/build
RUN mkdir ./data

# /workspace添加到python环境变量
ENV PYTHONPATH=/workspace:$PYTHONPATH

ADD ./start.sh ./start.sh
RUN chmod +x ./start.sh

CMD [ "bash", "./start.sh" ]