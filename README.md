# BOSS直聘自动化招聘系统

基于 DrissionPage + FastAPI + Vue 3 的 BOSS直聘自动化招聘系统，支持职位搜索、自动投递、自动聊天等功能。

## 技术栈

### 后端
- **FastAPI**: 高性能异步 Web 框架
- **DrissionPage**: 强大的浏览器自动化框架
- **MongoDB**: 文档型数据库
- **ddddocr**: 开源验证码识别库
- **uv**: 极速 Python 包管理器 (推荐)

### 前端
- **Vue 3**: 渐进式 JavaScript 框架
- **Vite**: 下一代前端构建工具
- **Element Plus**: Vue 3 组件库
- **TypeScript**: 类型安全的 JavaScript 超集
- **Pinia**: Vue 3 状态管理

## 项目结构

```
BOSS_RPA/
├── backend/                    # 后端服务
│   ├── app/                   # FastAPI应用
│   │   ├── api/              # API路由
│   │   ├── core/             # 核心配置
│   │   ├── models/           # MongoDB模型
│   │   ├── schemas/          # Pydantic模式
│   │   ├── services/         # 业务逻辑
│   │   └── main.py           # 应用入口
│   ├── rpa/                  # RPA自动化模块
│   │   ├── core/             # 核心模块
│   │   └── modules/          # 功能模块
│   │       ├── captcha/      # 验证码处理
│   │       ├── login/        # 登录模块
│   │       ├── job/          # 职位搜索
│   │       └── chat/         # 自动聊天
│   ├── pyproject.toml        # Python项目配置
│   └── requirements.txt      # Python依赖 (兼容pip)
├── frontend/                  # 前端应用
│   ├── src/
│   │   ├── api/             # API调用
│   │   ├── components/      # 组件
│   │   ├── views/           # 页面视图
│   │   ├── router/          # 路由配置
│   │   └── main.ts          # 应用入口
│   └── package.json         # Node依赖
├── data/                     # 数据目录
├── logs/                     # 日志目录
└── README.md
```

## 功能模块

### 已实现
- [x] 模块化项目架构
- [x] FastAPI 后端框架
- [x] Vue 3 前端框架
- [x] MongoDB 数据库集成
- [x] DrissionPage 浏览器管理
- [x] 滑块验证码识别 (ddddocr)
- [x] BOSS直聘登录模块
- [x] 职位搜索模块
- [x] 自动聊天模块

### 待完善
- [ ] 自动投递功能
- [ ] 任务调度系统
- [ ] 用户认证系统
- [ ] 数据统计分析

## 快速开始

### 环境要求
- Python 3.9+
- Node.js 16+
- MongoDB 4.4+
- uv (推荐) 或 pip

### 一键安装

```bash
# Windows: 运行安装脚本
install.bat

# 或手动安装
```

### 手动安装

#### 后端安装 (使用 uv)

```bash
# 安装 uv (如果未安装)
# Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# Linux/Mac: curl -LsSf https://astral.sh/uv/install.sh | sh

cd backend
uv sync                    # 安装依赖
cp .env.example .env       # 配置环境变量
```

#### 后端安装 (使用 pip)

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
```

#### 前端安装

```bash
cd frontend
npm install
```

### 启动服务

#### 使用启动脚本 (推荐)

```bash
# Windows
start.bat
```

#### 手动启动

```bash
# 后端 (uv)
cd backend
uv run python -m app.main

# 后端 (pip)
cd backend
python -m app.main

# 前端
cd frontend
npm run dev
```

## 配置说明

### 后端配置 (.env)
```bash
# 应用配置
APP_NAME=BOSS_RPA
DEBUG=True

# MongoDB配置
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=boss_rpa

# RPA配置
RPA_HEADLESS=False
RPA_TIMEOUT=30000

# BOSS直聘配置
BOSS_URL=https://www.zhipin.com
```

## 使用指南

### 1. 账户管理
在"账户管理"页面添加 BOSS直聘账户，系统会自动登录并保存 Cookie。

### 2. 职位搜索
创建"职位搜索"任务，配置搜索条件（关键词、城市、经验等），系统会自动搜索并保存职位信息。

### 3. 自动投递
根据保存的职位，批量进行自动投递操作。

### 4. 自动聊天
配置问候语模板，自动向HR打招呼。

## 注意事项

1. **验证码处理**: 当前使用 ddddocr 处理简单滑块验证码，复杂验证码可能需要人工处理。
2. **频率限制**: 建议设置合理的延迟，避免触发平台反爬机制。
3. **Cookie有效期**: Cookie有效期有限，需要定期刷新。
4. **法律合规**: 请确保使用本系统遵守相关法律法规和平台使用协议。

## 开发说明

### uv 常用命令

```bash
# 安装依赖
uv sync

# 添加新依赖
uv add package-name

# 添加开发依赖
uv add --dev package-name

# 运行项目
uv run python -m app.main

# 运行脚本
uv run script.py
```

### 添加新功能模块

### 添加新功能模块

1. 在 `backend/rpa/modules/` 下创建新模块
2. 继承 `BaseModule` 基类
3. 实现 `execute` 方法

```python
from rpa.core.base import BaseModule

class NewModule(BaseModule):
    def execute(self, **kwargs):
        # 实现具体功能
        return {"success": True, "data": ...}
```

### 添加新API接口

1. 在 `backend/app/api/` 下创建新路由文件
2. 在 `backend/app/api/__init__.py` 中注册路由

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/xxx", tags=["xxx"])

@router.get("/")
async def get_xxx():
    return {"data": ...}
```

## 常见问题

### Q: 登录失败怎么办？
A: 检查手机号密码是否正确，查看日志中的错误信息和截图。

### Q: 验证码识别失败？
A: ddddocr 对复杂验证码识别率有限，可以手动处理或训练模型。

### Q: 如何避免被封号？
A: 建议设置合理的延迟，避免高频操作，使用真实的浏览器指纹。

## License

MIT License

## 免责声明

本系统仅供学习交流使用，请勿用于非法用途。使用本系统造成的任何后果由使用者承担。
