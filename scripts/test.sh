# 测试

# 编译web前端
cd webui/web && npm run build && cd ../../

# 打包测试镜像
docker build -f ./docker/Dockerfile -t cosmosshadow/general-agent:test .

# 停止可能运行镜像
docker stop agent && docker rm agent

# 测试: 启动docker服务 & 映射单元测试代码 & 映射启动脚本 & 自动测试
docker run \
-p 3000:3000 \
-p 7777:7777 \
-v `pwd`/.env:/workspace/.env \
-v `pwd`/data:/workspace/data \
-v `pwd`/test:/workspace/test \
-v `pwd`/webui/server/test:/workspace/webui/server/test \
-v `pwd`/scripts/auto_test.sh:/workspace/start.sh \
--name=agent \
--privileged=true \
-d cosmosshadow/general-agent:test