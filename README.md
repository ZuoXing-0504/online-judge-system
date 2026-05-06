# 在线代码评测系统 (Online Code Judge)

一个功能完整的轻量级在线代码评测系统，支持用户注册登录、题目管理、Python 代码提交和实时异步评测。

## 系统架构

```
Client (Swagger UI)
  │
  ▼
FastAPI (App) ──────▶ PostgreSQL (持久化存储)
  │                        ▲
  ▼                        │
Redis (消息队列) ────▶ arq Worker (异步评测引擎)
```

| 组件 | 说明 |
|------|------|
| FastAPI App | 提供 RESTful API，自动生成 Swagger 文档，处理 HTTP 请求 |
| PostgreSQL | 存储用户、题目、测试用例、提交记录 |
| Redis | 消息队列（arq），缓存评测任务 |
| arq Worker | 从 Redis 取任务，在沙箱中执行用户代码并记录结果 |

## 技术栈

| 组件 | 技术选型 | 说明 |
|------|----------|------|
| Web 框架 | FastAPI | 自动生成 Swagger 文档，原生异步支持 |
| ORM | SQLAlchemy 2.0 (async) | 异步数据库操作，不阻塞事件循环 |
| 数据库 | PostgreSQL 16 | 持久化存储 |
| 缓存/队列 | Redis 7 + arq | 轻量异步任务队列 |
| 鉴权 | JWT (python-jose) | 无状态认证 |
| 密码哈希 | passlib + bcrypt | 安全密码存储 |
| 评测引擎 | subprocess + resource | 资源受限的代码执行 |
| 容器化 | Docker Compose | 一键启动全部服务 |
| 测试 | pytest + httpx | 异步测试框架 |

## 项目结构

```
online-judge/
├── app/
│   ├── main.py                 # FastAPI 应用入口
│   ├── core/                   # 配置、数据库连接、安全、依赖注入、异常定义
│   ├── models/                 # SQLAlchemy 数据模型（5 张表）
│   ├── schemas/                # Pydantic 请求/响应 Schema
│   ├── api/v1/                 # API 路由层
│   │   ├── auth.py             # 注册/登录
│   │   ├── users.py            # 用户信息
│   │   ├── problems.py         # 题目 CRUD + 测试用例管理
│   │   ├── submissions.py      # 提交代码 + 查看结果
│   │   └── admin.py            # 管理员接口
│   ├── services/               # 业务逻辑层
│   │   ├── auth_service.py     # 认证逻辑
│   │   ├── user_service.py     # 用户管理
│   │   ├── problem_service.py  # 题目管理
│   │   ├── submission_service.py # 提交管理
│   │   └── judge_service.py    # 评测编排
│   └── judge/                  # 评测引擎
│       ├── executor.py         # subprocess 代码执行
│       ├── sandbox.py          # 跨平台资源限制
│       ├── comparator.py       # 输出比对
│       └── worker.py           # arq Worker 配置
├── tests/                      # 测试用例
├── alembic/                    # 数据库迁移
├── docker-compose.yml          # Docker 编排
├── Dockerfile                  # 应用镜像
└── requirements.txt            # Python 依赖
```

## 数据库设计

5 张表，全部使用 UUID 主键：

| 表名 | 说明 | 关键字段 |
|------|------|----------|
| users | 用户表 | username, email, hashed_password, role |
| problems | 题目表 | title, slug, description, difficulty, time_limit_ms, memory_limit_kb |
| test_cases | 测试用例表 | problem_id, input, expected_output, is_sample |
| submissions | 提交记录表 | user_id, problem_id, code, status |
| submission_test_results | 测试点结果 | submission_id, test_case_id, status, output |

## 评测状态流转

```
用户提交代码
  │
  ▼
status: pending ──▶ Redis 入队
  │
  ▼
Worker 取出任务
  │
  ▼
status: running ──▶ 逐个测试点执行
  │                  (subprocess + resource 限制)
  ▼
汇总结果:
  - accepted              (全部通过)
  - wrong_answer          (输出不匹配)
  - time_limit_exceeded   (超时)
  - runtime_error         (运行错误)
```

## 快速开始

### 前置要求

- Docker & Docker Compose
- （可选）Python 3.12+ 用于本地开发

### 一键启动

```bash
git clone <repo-url>
cd online-judge
cp .env.example .env
docker compose up --build
```

### 访问服务

- **API 文档 (Swagger)**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/api/v1/health

### 使用流程

1. 在 Swagger 页面执行 `POST /api/v1/auth/register` 注册用户
2. 执行 `POST /api/v1/auth/login` 登录，获取 Token
3. 复制 Token，点击页面右上角 "Authorize" 粘贴认证
4. 管理员创建题目：`POST /api/v1/problems` + `POST /api/v1/problems/{slug}/test-cases`
5. 用户提交代码：`POST /api/v1/submissions`
6. 查看评测结果：`GET /api/v1/submissions/{id}`

## 本地开发（不使用 Docker）

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 需要本地运行 PostgreSQL 和 Redis，并配置 .env
cp .env.example .env

# 数据库迁移
alembic upgrade head

# 启动 API 服务（终端 1）
uvicorn app.main:app --reload

# 启动 Worker（终端 2）
arq app.judge.worker.WorkerSettings
```

## 运行测试

```bash
# 需要创建测试数据库 online_judge_test
pytest -v --cov=app
```

## 设计决策

**为什么选择 async SQLAlchemy？**
同步 SQLAlchemy 会阻塞 FastAPI 的事件循环，同一时刻只能处理一个数据库请求。async 版本配合 asyncpg 驱动可以并发处理多个数据库操作，充分利用异步 I/O。

**为什么用 arq 而不是 Celery？**
arq 是纯 async 的 Redis 队列，配置简单（只需一个类），与 FastAPI 异步哲学一致。Celery 组件多、配置重，对于这个规模的项目来说是过度设计。

**为什么用 subprocess 而不是 Docker SDK？**
Docker SDK 需要管理镜像、挂载 socket，复杂度高。subprocess 配合 resource.setrlimit 能在 Linux 上实现有效的资源隔离。面试中可以讨论："生产环境可以用 Docker 或 gVisor 获得更强的隔离"——这展示了技术选型的成熟思考。

**为什么用 UUID 主键？**
自增 ID 会泄露用户量、提交量等信息。UUID 防信息泄露，也便于未来分布式扩展。

**为什么分 Router → Service → Model 三层？**
路由层保持薄（只做参数校验和 HTTP 响应），业务逻辑集中在 Service 层，可以独立测试、可被多个路由和 Worker 复用。

## API 接口速览

| 方法 | 路径 | 说明 | 权限 |
|------|------|------|------|
| POST | /api/v1/auth/register | 注册 | 公开 |
| POST | /api/v1/auth/login | 登录 | 公开 |
| GET | /api/v1/users/me | 查看个人信息 | 登录 |
| PATCH | /api/v1/users/me | 修改个人信息 | 登录 |
| GET | /api/v1/problems | 题目列表（分页+筛选） | 公开 |
| GET | /api/v1/problems/{slug} | 题目详情 | 公开 |
| POST | /api/v1/problems | 创建题目 | 管理员 |
| PUT | /api/v1/problems/{slug} | 更新题目 | 管理员 |
| DELETE | /api/v1/problems/{slug} | 删除题目 | 管理员 |
| GET | /api/v1/problems/{slug}/test-cases | 查看测试用例 | 管理员 |
| POST | /api/v1/problems/{slug}/test-cases | 添加测试用例 | 管理员 |
| POST | /api/v1/submissions | 提交代码 | 登录 |
| GET | /api/v1/submissions | 提交记录列表 | 登录 |
| GET | /api/v1/submissions/{id} | 提交详情+测试结果 | 登录 |
| GET | /api/v1/admin/users | 用户列表 | 管理员 |
| PATCH | /api/v1/admin/users/{id}/role | 修改用户角色 | 管理员 |
| GET | /api/v1/health | 健康检查 | 公开 |

## 未来改进方向

- 支持更多编程语言（C++、Java、Go）
- Docker 沙箱替代 subprocess 增强安全隔离
- WebSocket 实时推送评测状态
- 竞赛模式（限时比赛 + 排行榜）
- 前端页面（Vue/React）
- CI/CD 自动化测试和部署

## 许可证

MIT License
