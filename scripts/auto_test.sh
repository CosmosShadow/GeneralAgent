# docker自动测试脚本，给docker用的，非人工操作

# load env
if [ -f /workspace/.env ]; then
  export $(grep -v '^#' /workspace/.env | sed 's/^export //g' | xargs)
fi

# start server
cd /workspace/webui/server/server
poetry run uvicorn app:app --host 0.0.0.0 --port 7777 > /dev/null 2>&1 &

# start web
cd /workspace/webui/web
nohup serve -s build &
cd ../../../

export LLM_CACHE='yes'

# global unit test
cd test
poetry pytest -s -v
cd ..

# test server
cd webui/server/test
poetry pytest -s -v
cd ../../../