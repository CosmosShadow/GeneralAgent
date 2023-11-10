cd /workspace/GeneralAgent/webui/server/server
nohup uvicorn app:app --host 0.0.0.0 --port 7777 & 

cd /workspace/GeneralAgent/webui/web
nohup npm run build &