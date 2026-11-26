# Oh-My-Agent
> Tauri + FastAPI 双端会话持久化大模型对话客户端，本地SQLite缓存，云端MySQL存储会话记录

## ✨ 项目简介
Oh-My-Agent 是一个面向个人使用的大模型对话应用。
客户端基于 Tauri 开发，一套代码可打包桌面端、Android 移动端；后端使用 FastAPI 异步服务，封装大模型API调用，搭配 LangChain 做上下文管理。
核心特性：**双端存储会话**，本地 SQLite 缓存对话记录（断网可查看历史），云端 MySQL 持久化保存，支持会话增量同步。
API密钥统一托管在后端环境变量，客户端不持有密钥，规避密钥泄露风险。

## 功能介绍

### 基础AI会话
项目提供了基础的AI对话，类似于手机上的主流的AI软件的会话方式，我们提供会话隔离的功能，不同会话之间的上下文不会互相影响。

### 服务器工作区
我们在服务器上的某个文件夹内，提供了用户工作区，用户可以将文件在该区域存储起来，该区域的文件可以是用户上传的，也可以是模型自主创建的。用户可以随时从服务器上将工作区的文件下载下来


## 🧩 技术栈
### 客户端
- Tauri 2.0
- 前端：React
- 本地存储：SQLite
- 通信：SSE 流式输出

### 后端
- FastAPI + Uvicorn
- LangChain
- MySQL
- mysql-connector-python
- python-dotenv
- 进程守护：systemd
- 反向代理：Nginx

## 📂 项目结构
```
oh-my-agent/
├── backend/                # FastAPI后端
│   ├── app/
│   │   ├── api/            # 接口路由
│   │   ├── config/         # 配置读取
│   │   ├── services/       # 业务逻辑
│   │   ├── schemas/        # Pydantic校验模型
│   │   ├── db/             # 数据库连接
│   │   └── common/         # 公共工具、异常处理
│   ├── scripts/            # 初始化SQL脚本
│   ├── .env
│   └── requirements.txt
└── client/                 # Tauri客户端
```

## 🚀 部署运行
### 后端部署
1. 进入后端目录，创建虚拟环境
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
2. 复制 `.env` 配置文件，填入大模型API密钥、数据库信息
```env
# .env
LLM_API_KEY=xxx
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASS=xxx
DB_NAME=oh_my_agent
```
3. 执行初始化脚本，创建数据库表
4. 启动服务
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```
> 生产环境配合 systemd 实现崩溃自动重启

### 客户端开发
1. 进入 client 目录，安装依赖
```bash
cd client
npm install
```
2. 开发调试
```bash
npm run tauri dev
```
3. 打包
```bash
npm run tauri build
```

## 📌 核心能力
- 流式对话（SSE），打字机效果
- 会话管理：新建、删除、查看历史对话
- 本地SQLite缓存 + 云端MySQL双存储，联网自动同步
- 后端统一转发大模型请求，密钥不暴露给前端
- 支持LangChain上下文组装，后续可扩展工具调用、Agent能力

## 📜 License
MIT License

---
