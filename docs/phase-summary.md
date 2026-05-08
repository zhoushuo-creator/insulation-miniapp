# 保温材料智能推荐系统 — 阶段总记录

## 项目概述

三端系统（FastAPI 后端 + Vue3 管理后台 + uni-app 小程序），实现保温材料的产品管理、AI 智能推荐、订单询价功能。

| 环境 | 路径 / 地址 |
|------|------------|
| 项目根目录 | `D:\Desktop\insulation-miniapp` (D 盘) |
| Python venv | `backend\.venv` |
| PostgreSQL | Docker `pgvector/pgvector:pg16`，端口 5433 |
| 后端 | `http://localhost:8000` |
| API 文档 | `http://localhost:8000/docs` |
| 管理后台 | `http://localhost:3000` |
| 缓存目录 | `E:\insulation-cache\` (pip / npm) |

---

## Phase 1 — 基础设施搭建

**目标**：三端骨架跑通

### 成果

| 层 | 内容 |
|----|------|
| 数据库 | PostgreSQL 16 + pgvector + pg_trgm，12 张 ORM 表自动建表 |
| 后端 | FastAPI 启动，全局 CORS / 异常处理 / JWT 安全组件 / 日志 |
| 管理后台 | Vue3 + Element Plus + Vue Router + Pinia + Axios，侧边栏导航 |
| 小程序 | uni-app (Vue 2) + uView UI，4 个 tab 页，Vuex 状态管理 |

### 表结构 (12 张)

`users` `products` `product_variants` `product_categories` `application_scenarios`
`product_scenario` `product_embeddings` `document_chunks` `chat_sessions`
`chat_messages` `orders` `order_items` `addresses`

### 启动命令

```bash
cd backend && docker compose up -d db
cd backend && source .venv/Scripts/activate && uvicorn app.main:app --reload --port 8000
cd admin && npm run dev
```

---

## Phase 2 — 产品核心数据

**目标**：产品 / 分类 CRUD 三端打通

### 后端新增

| 文件 | 说明 |
|------|------|
| `app/schemas/product.py` | ProductCreate/Update/Read, CategoryCreate/Update/Read, Variant, Scenario, ProductListResponse |
| `app/services/product.py` | 多维度筛选 (分类/场景/关键词/厚度/密度/防火等级/温度) + 分页排序 + 搜索 + 推荐 |
| `app/services/category.py` | 分类树递归构建 + CRUD + 子分类产品聚合 + 场景管理 |
| `app/services/seed.py` | 8 大类 30 子类 + 8 个应用场景，启动时自动种子 |
| `app/api/v1/endpoints/products.py` | 7 个端点：列表 / 推荐 / 搜索 / 详情 / 创建 / 更新 / 删除 |
| `app/api/v1/endpoints/categories.py` | 分类 + 场景 CRUD，分类树 + 分类下产品 |
| `app/api/v1/router.py` | 新增 `/dashboard` 统计端点 |

### 种子数据

**8 大类**：岩棉板(4)、玻璃棉(4)、硅酸铝(4)、聚氨酯(3)、挤塑板(3)、橡塑海绵(2)、气凝胶(3)、保温砂浆(3) → 共 34 条

**8 场景**：屋顶保温 / 外墙保温 / 管道保温 / 工业窑炉 / 冷库保温 / 暖通空调 / 船舶保温 / 储罐保温

### 前端

| 页面 | 位置 | 功能 |
|------|------|------|
| 产品管理 | `admin/views/products/` | 表格 + 搜索 + 筛选 + 新增/编辑/详情对话框 + 变体管理 + 场景关联 |
| 分类管理 | `admin/views/categories/` | 树形控件 + 详情面板 + 添加/编辑/删除 |
| 数据概览 | `admin/views/dashboard/` | 4 张统计卡片，实时 API |
| 首页(更新) | `miniapp/pages/index/` | 推荐产品卡片 |
| 产品列表 | `miniapp/pagesA/pages/product-list/` | 搜索 + 分类筛选 + 排序 + 分页加载 |
| 产品详情 | `miniapp/pagesA/pages/product-detail/` | 轮播图 + 参数 + 变体表格 + 加入询价 |
| 产品卡片 | `miniapp/components/product-card/` | 可复用卡片组件 |

### Phase 2 审查修复 (4 bugs)

1. 分类序列化 `children` 与 ORM 懒加载冲突 → `field_validator` 兜底
2. 排序不支持 `_asc/_desc` 后缀 → 解析方向
3. `product-detail` 用 `switchTab` 跳非 tab 页 → 改 `navigateTo`
4. 删除根分类时产品外键冲突 → 无父级时移至兄弟分类

---

## Phase 3 — AI 智能对话与推荐

**目标**：RAG 管线打通 — 用户需求 → 向量检索 → DeepSeek 生成推荐

### 后端新增

| 文件 | 说明 |
|------|------|
| `app/services/embedding.py` | 通义千问 DashScope text-embedding-v3，1024 维向量生成 |
| `app/services/rag.py` | RAG 核心：嵌入→pgvector 余弦搜索→构造 Prompt→DeepSeek 生成→保存会话 |
| `app/services/embedding_pipeline.py` | 批量产品向量化，支持增量 |
| `app/api/v1/endpoints/ai_chat.py` | 6 个端点：对话 / SSE 流式 / 推荐 / 会话列表 / 会话详情 / 生成嵌入 |

### RAG 流程

```
用户提问 "外墙保温A1级防火材料"
  → DashScope 嵌入(1024维)
  → pgvector <=> 余弦距离搜索
  → GROUP BY 去重，取 MIN(distance)
  → 匹配产品加入 Prompt
  → DeepSeek 生成 → 返回产品卡片 + 推荐理由
```

### 端点

| 端点 | 功能 |
|------|------|
| `POST /ai/chat` | AI 对话 (RAG) |
| `POST /ai/chat/stream` | SSE 流式输出 |
| `POST /ai/recommend` | 智能推荐 |
| `GET /ai/sessions` | 对话历史 |
| `GET /ai/sessions/{id}` | 会话详情 |
| `POST /ai/generate-embeddings` | 产品嵌入生成 |

### 前端

| 页面 | 功能 |
|------|------|
| `admin/views/ai-chat/` | 对话历史列表 + 消息详情面板 |
| `miniapp/pagesB/pages/ai-chat/` | AI 聊天界面 + 快捷问题 + 产品卡片引用 + 跳转详情 |
| `miniapp/pagesB/pages/smart-recommend/` | 输入需求 → 匹配产品列表 |

### Phase 3 审查修复 (3 bugs)

1. 向量搜索同一产品多嵌入占位 → `GROUP BY + MIN(distance)` 子查询去重
2. `embedding_pipeline.py` 动态 `__import__` → 正常 `from sqlalchemy import delete`
3. `_semantic_search` 无异常处理 → try/catch

---

## Phase 4 — 订单与询价

**目标**：询价清单 → 订单创建 → 状态流转，三端同步

### 后端新增

| 文件 | 说明 |
|------|------|
| `app/schemas/order.py` | OrderCreate/Read/ListResponse, OrderItemRead, AddressCreate/Update/Read |
| `app/services/order.py` | 订单 CRUD + 状态流转 (pending→paid→shipped→completed / cancelled) + 收货地址 CRUD |
| `app/api/v1/endpoints/orders.py` | 7 个端点 + 地址 CRUD |

### 端点

| 端点 | 功能 |
|------|------|
| `POST /orders` | 创建订单 |
| `GET /orders` | 订单列表 (分页 + 状态筛选) |
| `GET /orders/{id}` | 订单详情 (含 OrderItem) |
| `PUT /orders/{id}/cancel` | 取消订单 |
| `PUT /orders/{id}/status` | 状态流转 (管理端) |
| `GET/POST/PUT/DELETE /addresses` | 收货地址 CRUD |

### 前端

| 页面 | 位置 | 功能 |
|------|------|------|
| 订单管理 | `admin/views/orders/` | 表格 + 状态筛选 + 一键流转 |
| 询价清单 (更新) | `miniapp/pages/cart/` | 勾选 → 提交订单 API → 清空购物车 → 跳转订单页 |
| 我的订单 | `miniapp/pagesB/pages/order/` | 订单列表 + 取消 |

### Phase 4 审查修复

1. 购物车字段 `product_name`/`price` 与 store 不一致 → 统一为 `name`/`reference_price`
2. 地址 NOT NULL 列传 None → 服务层默认空字符串

---

## API 端点总览 (Phase 1-4)

```
/api/v1/
├── dashboard           GET  数据概览
├── products            GET  产品列表(多维度筛选)
│   /recommended        GET  推荐产品
│   /search             GET  关键词搜索
│   /{id}               GET  产品详情
│                       POST 创建产品
│                       PUT  更新产品
│                       DELETE 删除产品
├── categories          GET  分类树
│   /{id}               GET  单分类
│   /{id}/products      GET  分类下产品
│                       POST 创建分类
│                       PUT  更新分类
│                       DELETE 删除分类
├── scenarios           GET/POST 场景列表/创建
│   /{id}               PUT/DELETE 场景更新/删除
├── ai/chat             POST AI对话
│   /stream             POST SSE流式
│   /recommend          POST 智能推荐
│   /sessions           GET  对话历史
│   /sessions/{id}      GET  会话详情
│   /generate-embeddings POST 生成嵌入
├── orders              GET/POST 订单列表/创建
│   /{id}               GET  订单详情
│   /{id}/cancel        PUT  取消
│   /{id}/status        PUT  状态流转
├── addresses           GET/POST 地址列表/创建
│   /{id}               PUT/DELETE 地址更新/删除
├── auth                (stub)
└── upload              (stub)
```

## 当前进度

```
Phase 1  ████████████  基础设施    ✅
Phase 2  ████████████  产品数据    ✅
Phase 3  ████████████  AI 对话     ✅
Phase 4  ████████████  订单询价    ✅
Phase 5  ░░░░░░░░░░░░  认证/OCR    待做
         └── 80% ──┘
```

## Phase 5 待实现

- 微信小程序登录 (`wx.login` → JWT)
- 管理后台扫码登录 (微信开放平台)
- 文件上传 (产品图片 + 纸质资料)
- OCR 识别 → chunk → 向量嵌入管线
- 管理员权限控制恢复
