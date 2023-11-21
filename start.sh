# load env
if [ -f /workspace/.env ]; then
  export $(grep -v '^#' /workspace/.env | sed 's/^export //g' | xargs)
fi

cd /workspace/webui/server/server
# poetry shell, python app.py
poetry run uvicorn app:app --host 0.0.0.0 --port 7777 > /dev/null 2>&1 &

cd /workspace/webui/web
serve -s build