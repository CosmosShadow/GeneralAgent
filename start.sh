cd /workspace/webui/server/server
nohup uvicorn app:app --host 0.0.0.0 --port 7777 & 

cd /workspace/webui/web
nohup serve -s build &