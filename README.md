# Travel Agents - 智能旅行助手

基于 LangGraph 多智能体架构的智能旅行规划系统，通过 AI Agent 协作为用户生成个性化旅行计划。

## 项目架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Vue 3)                        │
│    Ant Design Vue + 高德地图 + PDF 导出                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                LangGraph Supervisor Agent                    │
│                    (协调 & 整合输出)                          │
└─────────────────────────────────────────────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Attraction Agent│  │  Weather Agent  │  │   Hotel Agent   │
│    景点规划      │  │    天气查询      │  │    酒店推荐      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
          │                    │                    │
          └────────────────────┼────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                高德地图 MCP Server                           │
│         (地图搜索 / 天气查询 / POI 数据)                      │
└─────────────────────────────────────────────────────────────┘
```

## 技术栈

### 后端
- **LangGraph** - 多智能体编排框架
- **LangChain** - LLM 应用开发框架
- **FastAPI** - 高性能 Python Web 框架
- **PostgreSQL** - Agent 记忆持久化
- **高德地图 MCP Server** - 地理位置服务

### 前端
- **Vue 3** + **TypeScript**
- **Vite** - 构建工具
- **Ant Design Vue** - UI 组件库
- **高德地图 JS API** - 地图可视化
- **jsPDF** + **html2canvas** - PDF 导出

## 功能特性

- **智能行程规划** - 根据目的地、日期、偏好生成多日行程
- **天气查询** - 实时获取目的地天气预报
- **景点推荐** - 基于用户偏好推荐热门景点
- **酒店推荐** - 按预算和位置推荐合适住宿
- **预算估算** - 自动计算旅行费用
- **PDF 导出** - 将行程计划导出为 PDF 文件
- **地图可视化** - 在地图上展示行程路线

## 项目结构

```
Travel-agents/
├── backend/
│   ├── app/
│   │   ├── agents/           # 多智能体模块
│   │   │   ├── multi_agents.py   # Agent 定义与编排
│   │   │   ├── tools.py          # MCP 工具加载
│   │   │   └── prompt.py         # Agent 提示词
│   │   ├── api/              # API 路由
│   │   │   ├── main.py           # FastAPI 应用入口
│   │   │   └── routes/           # 各功能路由
│   │   ├── models/           # 数据模型
│   │   ├── services/         # 业务服务
│   │   └── config.py         # 配置管理
│   ├── run.py                # 启动脚本
│   └── .env                  # 环境变量
├── frontend/
│   ├── src/
│   │   ├── views/            # 页面组件
│   │   ├── services/         # API 服务
│   │   └── types/            # TypeScript 类型
│   └── package.json
└── requirements.txt          # Python 依赖
```

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- uv (Python 包管理器)

### 1. 克隆项目

```bash
git clone https://github.com/KAI3zZ/Travel_Agents.git
cd Travel_Agents
```

### 2. 配置环境变量

创建 `backend/.env` 文件：

```env
# 高德地图 API
AMAP_API_KEY=your_amap_api_key

# LLM 配置 (支持 OpenAI 兼容接口)
LLM_API_KEY=your_llm_api_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL_ID=gpt-4

# Unsplash API (可选，用于获取图片)
UNSPLASH_ACCESS_KEY=your_unsplash_key

# PostgreSQL 数据库
DATABASE_URL=postgresql://user:password@localhost:5432/agents_db
```

### 3. 启动后端

```bash
cd backend

# 创建虚拟环境并安装依赖
uv venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

uv pip install -r ../requirements.txt

# 启动服务
python run.py
```

后端服务将在 `http://localhost:8000` 启动。

### 4. 启动前端

```bash
cd frontend

npm install
npm run dev
```

前端服务将在 `http://localhost:5173` 启动。

## API 文档

启动后端后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要接口

| 接口 | 方法 | 描述 |
|------|------|------|
| `/api/trip/plan` | POST | 生成旅行计划 |
| `/api/poi/search` | POST | 搜索 POI |
| `/api/map/route` | POST | 路线规划 |
| `/api/map/weather` | GET | 查询天气 |

### 请求示例

```bash
curl -X POST http://localhost:8000/api/trip/plan \
  -H "Content-Type: application/json" \
  -d '{
    "city": "北京",
    "start_date": "2025-06-01",
    "end_date": "2025-06-03",
    "travel_days": 3,
    "transportation": "公共交通",
    "accommodation": "经济型酒店",
    "preferences": ["历史文化", "美食"],
    "free_text_input": "希望多安排一些博物馆"
  }'
```

## 获取 API Keys

- **高德地图 API**: https://lbs.amap.com/
- **OpenAI API**: https://platform.openai.com/
- **Unsplash API**: https://unsplash.com/developers

## 许可证

MIT License
