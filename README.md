# 保温材料智能推荐系统

三端系统：**FastAPI 后端** + **Vue3 管理后台** + **uni-app 微信小程序**，实现保温材料的产品管理、AI 智能推荐（RAG）、询价下单。

## 架构

```
insulation-miniapp/
├── backend/    FastAPI + PostgreSQL + pgvector + DeepSeek + DashScope
├── admin/      Vue3 + Element Plus 管理后台
├── miniapp/    uni-app 微信小程序 (uView UI 2.0)
└── docs/       阶段记录
```

## 功能

| 模块 | 功能 |
|------|------|
| 产品管理 | 8大类30子类保温材料，多维筛选、变体管理、场景标签 |
| AI 智能顾问 | RAG 对话：用户需求 → 向量检索 → DeepSeek 推荐产品 |
| 智能推荐 | 输入应用场景 → 语义匹配产品列表 |
| 询价下单 | 加入清单 → 提交询价 → 订单管理 |
| 管理后台 | 产品/分类/订单 CRUD、数据仪表盘 |
| 微信登录 | wx.login → JWT 认证 |
| 扫码登录 | 管理后台二维码 → 小程序扫码确认 |

## 技术栈

- **后端**: Python 3.13 + FastAPI + SQLAlchemy 2.0 + PostgreSQL 16 + pgvector
- **AI**: DeepSeek Chat + DashScope text-embedding-v3 (1024维)
- **管理后台**: Vue 3.4 + TypeScript + Element Plus 2.7 + Pinia
- **小程序**: uni-app (Vue 2) + uView UI 2.0 + Vuex

## 快速启动

### 1. 启动数据库

```bash
cd backend
docker compose up -d db
```

### 2. 启动后端

```bash
cd backend
.venv\Scripts\activate.bat          # Windows
uvicorn app.main:app --reload --port 8000
```

API 文档: http://localhost:8000/docs

### 3. 启动管理后台

```bash
cd admin
npm install
npm run dev
```

打开 http://localhost:3000

### 4. 启动小程序

用 HBuilderX 打开 `miniapp/` 目录 → 运行到微信开发者工具

### 环境变量

复制 `backend/.env.example` 为 `backend/.env`，填入 API Key：

```env
DEEPSEEK_API_KEY=sk-...
DASHSCOPE_API_KEY=sk-...
DATABASE_URL=postgresql+psycopg://postgres:postgres@127.0.0.1:5433/insulation_db
```

## API 端点总览

```
/api/v1/
├── dashboard          GET   数据概览
├── products           GET   产品列表 (多维筛选)
│   /recommended       GET   推荐产品
│   /search            GET   关键词搜索
├── categories         GET   分类树
├── scenarios          GET   应用场景
├── ai/chat            POST  AI 对话 (RAG)
│   /recommend         POST  智能推荐
│   /sessions          GET   对话历史
├── orders             GET   订单列表
│                      POST  创建订单
├── addresses          GET   收货地址
├── auth/wx-login      POST  微信登录
└── upload             POST  文件上传
```

## 进度

```
Phase 1  基础设施    ✅
Phase 2  产品数据    ✅
Phase 3  AI 对话     ✅
Phase 4  订单询价    ✅
Phase 5  认证/上传   ✅
```
