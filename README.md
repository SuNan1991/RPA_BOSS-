# BOSS直聘自动化招聘系统

基于 DrissionPage + FastAPI + Vue 3 的 BOSS直聘自动化招聘系统，支持职位搜索、自动投递、自动聊天等功能。

## 技术栈

### 后端
- **FastAPI**: 高性能异步 Web 框架
- **DrissionPage**: 强大的浏览器自动化框架
- **SQLite**: 轻量级关系型数据库
- **aiosqlite**: 异步 SQLite 驱动
- **ddddocr**: 开源验证码识别库
- **uv**: 极速 Python 包管理器 (推荐)

### 前端
- **Vue 3**: 渐进式 JavaScript 框架
- **Vite**: 下一代前端构建工具
- **Tailwind CSS**: 实用优先的 CSS 框架
- **TypeScript**: 类型安全的 JavaScript 超集
- **Pinia**: Vue 3 状态管理

## 项目结构

```
BOSS_RPA/
├── backend/                    # 后端服务
│   ├── app/                   # FastAPI应用
│   │   ├── api/              # API路由
│   │   ├── core/             # 核心配置
│   │   ├── schemas/          # Pydantic模式
│   │   ├── services/         # 业务逻辑
│   │   └── main.py           # 应用入口
│   ├── data/                 # SQLite数据库文件
│   ├── rpa/                  # RPA自动化模块
│   │   ├── core/             # 核心模块
│   │   └── modules/          # 功能模块
│   │       ├── captcha/      # 验证码处理
│   │       ├── login/        # 登录模块
│   │       ├── job/          # 职位搜索
│   │       └── chat/         # 自动聊天
│   ├── scripts/              # 工具脚本
│   │   └── migrate_mongodb_to_sqlite.py  # 数据迁移脚本
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
├── logs/                     # 日志目录
├── docs/                     # 文档中心
│   ├── guides/              # 开发和部署指南
│   ├── troubleshooting/     # 故障排查
│   ├── changelog/           # 变更记录
│   ├── features/            # 功能实现文档
│   └── bugs/                # 问题修复记录
└── README.md
```

## 功能模块

### 已实现
- [x] 模块化项目架构
- [x] FastAPI 后端框架
- [x] Vue 3 前端框架
- [x] SQLite 数据库集成
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

## 📚 文档中心

完整的文档请访问 [docs/](./docs/) 目录，包含：

### 📖 开发指南
- **[开发指南](./docs/guides/development.md)** - Claude Code 开发指南、项目架构和最佳实践
- **[部署指南](./docs/guides/deployment.md)** - MongoDB 到 SQLite 迁移步骤
- **[脚本使用指南](./docs/guides/scripts.md)** - 批处理脚本使用方法

### 🔧 故障排查
- **[错误指南](./docs/troubleshooting/error-guide.md)** - 常见错误预防
- **[启动警告](./docs/troubleshooting/startup-warnings.md)** - 已知启动问题和解决方案

### 📝 变更记录
- **[CHANGELOG](./docs/changelog/CHANGELOG.md)** - 完整的版本变更日志
- **[数据库迁移](./docs/changelog/migration.md)** - MongoDB 到 SQLite 迁移摘要
- **[端口更新](./docs/changelog/port-update.md)** - 端口配置更新说明

### ✨ 功能实现
- **[安全登录 UI](./docs/features/secure-login-ui.md)** - BOSS 安全登录界面实现详情

### 🐛 问题修复
- **[DrissionPage 修复](./docs/bugs/drissionpage-fixes.md)** - DrissionPage 相关问题修复
- **[错误修复摘要](./docs/bugs/error-fixes.md)** - 错误修复汇总

> 📖 **更多文档**: 访问 [docs/INDEX.md](./docs/INDEX.md) 查看完整的文档索引。

## 配置说明

### 后端配置 (.env)
```bash
# 应用配置
APP_NAME=BOSS_RPA
DEBUG=True

# SQLite配置
SQLITE_DB_PATH=data/boss_rpa.db

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

## 数据库

### SQLite 数据库

应用使用 SQLite 作为数据库，数据文件位于 `backend/data/boss_rpa.db`。

#### 首次启动

首次启动时，应用会自动创建数据库文件并初始化表结构。

#### 从 MongoDB 迁移

如果你有现有的 MongoDB 数据，可以使用迁移脚本：

```bash
cd backend
python scripts/migrate_mongodb_to_sqlite.py
```

迁移前请确保：
1. MongoDB 正在运行
2. 已备份 MongoDB 数据
3. SQLite 数据库文件不存在（或已删除）

#### 数据备份

备份 SQLite 数据库只需复制文件：

```bash
cp backend/data/boss_rpa.db backend/data/boss_rpa.db.backup
```

## 注意事项

1. **验证码处理**: 当前使用 ddddocr 处理简单滑块验证码，复杂验证码可能需要人工处理。
2. **频率限制**: 建议设置合理的延迟，避免触发平台反爬机制。
3. **Cookie有效期**: Cookie有效期有限，需要定期刷新。
4. **法律合规**: 请确保使用本系统遵守相关法律法规和平台使用协议。

## 开发说明

### Git Hooks (代码质量保障)

本项目使用 [pre-commit](https://pre-commit.com/) 框架管理 Git hooks，自动在提交和推送时检查代码质量。

#### 一键安装 hooks

```bash
# 安装 pre-commit (使用 uv)
cd backend
uv sync --group dev

# 安装所有 Git hooks (pre-commit + commit-msg + pre-push)
pre-commit install --hook-type pre-commit --hook-type commit-msg --hook-type pre-push
```

或者使用 pip:

```bash
pip install pre-commit
pre-commit install --hook-type pre-commit --hook-type commit-msg --hook-type pre-push
```

#### Hook 说明

| Hook 阶段 | 检查内容 | 运行时机 |
|-----------|---------|---------|
| **pre-commit** | 文件格式 (空白、换行、YAML/JSON 校验)、Python lint + format (ruff)、大文件检测、密钥检测 | 每次 `git commit` |
| **commit-msg** | 提交信息格式 ([Conventional Commits](https://www.conventionalcommits.org/)) | 每次 `git commit` |
| **pre-push** | Python 测试 (pytest)、Python 类型检查 (mypy)、前端类型检查 (vue-tsc) | 每次 `git push` |

#### Conventional Commits 格式

提交信息必须遵循以下格式:

```
type(scope): description

# 示例
feat(login): 添加手机验证码登录支持
fix(api): 修复任务列表分页错误
docs: 更新部署文档
chore: 更新依赖版本
refactor(rpa): 重构浏览器管理模块
```

允许的类型: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`, `build`, `revert`

#### 跳过 hooks (紧急情况)

```bash
# 跳过 pre-commit 和 commit-msg hooks
git commit --no-verify -m "emergency fix"

# 跳过 pre-push hooks
git push --no-verify
```

#### 更新 hook 版本

```bash
pre-commit autoupdate
```

#### 手动运行所有 hooks

```bash
# 对所有文件运行 pre-commit hooks
pre-commit run --all-files

# 运行特定 hook
pre-commit run ruff --all-files
pre-commit run ruff-format --all-files
```

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
