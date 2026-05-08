# 第一阶段完成记录

## 当前运行状态

| 服务 | 地址 | 启动方式 |
|------|------|---------|
| PostgreSQL 16 + pgvector | `127.0.0.1:5433` | `cd backend && docker compose up -d db` |
| FastAPI 后端 | `http://localhost:8000` | `cd backend && source .venv/Scripts/activate && uvicorn app.main:app --reload --port 8000` |
| API 文档 | `http://localhost:8000/docs` | 同上，自动生成 |
| 管理后台 | `http://localhost:3000` | `cd admin && npm run dev` |

## 环境信息

- Python 3.13, venv 在 `backend/.venv`（D 盘）
- Node.js v24 在 D 盘
- PostgreSQL 通过 Docker 运行（数据在 `E:\docker\DockerDesktopWSL\disk\docker_data.vhdx`）
- 端口 5432 被原生 PostgreSQL 16 服务占用（未使用），Docker 版用 5433

## 数据库

```
数据库: insulation_db
用户: postgres / postgres
驱动: postgresql+psycopg (asyncpg 不兼容 Python 3.13 Windows)
扩展: vector 0.8.2 + pg_trgm 1.6 + plpgsql
```

## API Key

- DeepSeek: 已填入（对话生成）
- 通义千问 DashScope: 已填入（向量嵌入）
- 微信 AppID/Secret: 待填

## 项目结构

```
insulation-miniapp/
├── miniapp/          uni-app 小程序骨架
├── backend/          FastAPI 后端
│   ├── app/models/   12 张 ORM 表已创建
│   ├── app/api/      路由 + 端点 stub
│   └── app/services/ 业务逻辑待实现
└── admin/            Vue3 + Element Plus 管理后台骨架
```

## 已知问题

- asyncpg 不兼容 Python 3.13 → 改用 psycopg
- Windows 需 SelectorEventLoop → main.py 顶部已处理
- 原机 PostgreSQL 16 服务占用 5432 → Docker 映射 5433:5432
- 表通过 FastAPI lifespan create_all 自动建，未用 Alembic 迁移

## 下一阶段任务

1. 种子产品分类数据（8 大类 + 子类）
2. 产品 CRUD API 完整实现
3. 产品搜索/筛选端点
4. 管理后台产品管理页面
5. 小程序首页 + 列表 + 详情页
