# Server

FastAPI 后端服务，采用前后端分离架构。分层刻意贴近 SpringBoot，方便快速上手。

## 目录结构

```
server/
├── main.py                     # 启动类：创建 FastAPI 实例、注册中间件和路由
├── .env                        # 本地配置（已 gitignore）
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── router.py       # 路由聚合：统一挂载 /api/v1 下的模块
│   │       └── test.py         # Controller：/api/v1/test
│   ├── services/
│   │   └── test_service.py     # Service：业务逻辑
│   ├── schemas/
│   │   └── test.py             # DTO/VO：请求响应模型（Pydantic）
│   ├── models/                 # Entity：SQLAlchemy ORM 模型（待填充）
│   ├── db/                     # Repository/Mapper：数据库连接与 Session（待填充）
│   └── common/
│       ├── config.py           # 配置：application.yml 的替代
│       └── response.py         # 统一响应体 Result<T>
└── requirements.txt
```

## 与 SpringBoot 的对应关系

| SpringBoot | 本项目 | 说明 |
| --- | --- | --- |
| 启动类 `@SpringBootApplication` | `main.py` 的 `create_app()` | 创建应用、装配组件 |
| `application.yml` | `app/common/config.py` + `.env` | Pydantic Settings 读取配置 |
| `@RestController` | `app/api/v1/test.py` | 用 `APIRouter` 代替 |
| `@RequestMapping("/api/v1")` | `api_router` + `include_router(prefix=...)` | `router.py` 做聚合 |
| `@Service` | `app/services/*.py` | 普通函数/类，无需注解 |
| DTO / VO | `app/schemas/*.py` | Pydantic `BaseModel` |
| `@Entity` | `app/models/*.py` | SQLAlchemy 模型 |
| `@Repository` / Mapper | `app/db/` | SQLAlchemy Session/Engine |
| `Result<T>` | `app/common/response.py` | 泛型 `Result` |

一个请求的调用链：

```
main.py → api/v1/router.py → api/v1/test.py（Controller）
        → services/test_service.py（Service）
        → schemas/test.py（返回模型）
        → common/response.py（统一包装）
```

## 启动

```bash
cd server

# Windows（使用项目虚拟环境）
.venv\Scripts\python.exe main.py

# macOS / Linux
.venv/bin/python main.py
```

或者开发模式热重载：

```bash
.venv/Scripts/python.exe -m uvicorn main:app --reload
```

- 接口地址：<http://127.0.0.1:8000/api/v1/test>
- 接口文档（Swagger）：<http://127.0.0.1:8000/docs>

## 测试接口

```bash
curl http://127.0.0.1:8000/api/v1/test
```

```json
{"code":0,"message":"success","data":{"message":"Hello World"}}
```

## 新增一个模块

1. 在 `app/schemas/` 写数据模型；
2. 在 `app/services/` 写业务逻辑；
3. 在 `app/api/v1/` 新建 `<模块>.py`，用 `APIRouter` 定义接口；
4. 在 `app/api/v1/router.py` 中 `include_router` 注册。
