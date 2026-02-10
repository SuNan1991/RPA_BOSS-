# Proposal: BOSS Secure Login UI & Frontend Modernization

## Why

当前的 BOSS 直聘 RPA 系统前端存在以下问题：
1. **用户体验差**：多页面架构对于简单的 RPA 辅助工具过于复杂
2. **设计陈旧**：使用 Element Plus 默认样式，缺乏现代感
3. **登录流程不安全**：缺乏自动化检测防护，容易导致账号封禁
4. **状态管理混乱**：未登录用户也能访问功能页面，逻辑不清晰

现在需要重构为一个**现代化、极简、安全**的单页应用，聚焦于核心功能：账号状态显示和安全的辅助登录。

## What Changes

### 前端完全重构
- **BREAKING**: 删除所有现有页面（jobs, tasks, accounts, settings）
- **BREAKING**: 简化路由配置，只保留首页和登录后页面
- **NEW**: 实现极简主义单页应用，采用玻璃拟态设计风格
- **NEW**: 使用 Tailwind CSS + Headless UI 替代 Element Plus，更灵活的样式控制
- **NEW**: 原生支持亮色/暗色主题切换
- **NEW**: 响应式设计，适配桌面和移动端

### 安全登录系统
- **NEW**: 用户辅助登录流程（RPA 打开浏览器 → 用户扫码 → 保存会话）
- **NEW**: WebSocket 实时连接状态监控
- **NEW**: 账号信息展示（用户名、状态、连接时间）
- **NEW**: 反自动化检测设计（使用真实浏览器配置）

### 后端 API 优化
- **NEW**: `/api/auth/status` - 获取当前登录状态
- **NEW**: `/api/auth/login` - 启动 RPA 登录流程
- **NEW**: `/api/auth/logout` - 退出登录并清理会话
- **NEW**: `/ws/auth` - WebSocket 连接，实时推送登录状态
- **NEW**: RPA 服务层抽象，支持浏览器生命周期管理

### RPA 安全增强
- **NEW**: `BrowserManager` - 浏览器实例管理器
- **NEW**: `AntiDetection` - 反检测模块（配置真实 User-Agent、隐藏 WebDriver 特征）
- **NEW**: `SessionManager` - 会话持久化管理（SQLite 存储 Cookie）
- **NEW**: 登录超时机制（5 分钟未完成自动关闭浏览器）

## Capabilities

### New Capabilities

#### `boss-landing-page`
首页/登录引导页能力。提供极简的 Landing Page，展示系统介绍和账号状态，包含登录按钮。

**功能范围**：
- 显示当前系统状态（未登录/已登录）
- 展示登录账号信息（用户名、头像、连接时长）
- 提供登录/退出按钮
- 实时连接状态指示器（心跳检测）
- 支持亮色/暗色主题切换

#### `secure-rpa-login`
安全的 RPA 辅助登录能力。通过用户辅助的方式实现安全登录，避免自动化检测。

**功能范围**：
- RPA 自动启动浏览器并导航到 BOSS 直聘登录页
- 等待用户手动扫码或输入密码完成登录
- 登录成功后自动提取并保存 Cookie
- WebSocket 实时推送登录状态变化
- 超时自动关闭浏览器（5 分钟）
- 反自动化检测配置

#### `modern-ui-system`
现代化 UI 系统能力。提供极简、玻璃拟态风格的设计组件库。

**功能范围**：
- Tailwind CSS 样式系统配置
- 亮色/暗色主题切换机制
- 玻璃拟态效果组件（毛玻璃背景、模糊效果）
- 响应式布局系统
- 动画过渡效果

### Modified Capabilities

*无 - 本次变更不涉及修改现有能力规范（因为是完全重建）*

## Impact

### 代码影响

**前端**：
- 删除 `frontend/src/views/` 下所有现有页面
- 重写 `frontend/src/App.vue`、`frontend/src/router/index.ts`
- 新增 `frontend/src/composables/` - 组合式 API（useAuth、useTheme、useRPA）
- 新增 `frontend/src/components/` - UI 组件库
- 替换 Element Plus 为 Tailwind CSS + Headless UI
- 更新 `frontend/package.json` 依赖

**后端**：
- 新增 `backend/app/api/auth.py` - 认证相关 API
- 新增 `backend/app/services/rpa_service.py` - RPA 服务层
- 新增 `backend/rpa/modules/browser_manager.py` - 浏览器管理
- 新增 `backend/rpa/modules/anti_detection.py` - 反检测模块
- 更新 `backend/app/main.py` - 添加 WebSocket 支持

**数据库**：
- 新增 `sessions` 表 - 存储 BOSS 直聘会话信息（cookie、用户信息、过期时间）
- 新增 `login_logs` 表 - 登录日志记录

### 依赖变更

**前端新增**：
- `tailwindcss` - CSS 框架
- `@headlessui/vue` - 无样式 UI 组件
- `vue-use` - 组合式工具库
- `socket.io-client` - WebSocket 客户端

**后端新增**：
- `websockets` - WebSocket 支持（FastAPI 原生）
- 无需额外依赖，继续使用 DrissionPage

### 架构影响

**前端架构变化**：
```
旧架构：多页面应用（4 个页面）
新架构：单页应用（2 个视图 + 实时状态管理）

旧：Vue Router → Pages → Element Plus Components
新：Pinia Store → Composables → Tailwind Custom Components
```

**后端架构变化**：
```
新增 RPA 服务层：
   API Layer → RPA Service → Browser Manager → DrissionPage
                  ↓
            Anti Detection Module

新增 WebSocket 实时通信：
   Frontend ←→ WebSocket ←→ RPA Service
```

### 安全性影响

**提升**：
- ✅ 用户辅助登录降低自动化检测风险
- ✅ 会话持久化减少频繁登录
- ✅ 反检测配置隐藏自动化特征
- ✅ 超时机制防止浏览器泄漏

**风险**：
- ⚠️ Cookie 存储需要加密保护
- ⚠️ WebSocket 连接需要认证
- ⚠️ RPA 浏览器需要资源限制

### 性能影响

- ✅ 单页应用减少路由切换开销
- ✅ Tailwind CSS 按需生成，包体积更小
- ⚠️ WebSocket 长连接增加服务器资源占用
- ⚠️ RPA 浏览器实例占用内存（约 200-500MB）

### 用户体验影响

**提升**：
- ✅ 极简设计，降低学习成本
- ✅ 实时状态反馈，交互更流畅
- ✅ 玻璃拟态视觉效果更现代
- ✅ 暗色模式保护视力

**折衷**：
- ⚠️ 单页应用可能不适合复杂功能扩展
- ⚠️ 删除现有页面导致功能暂时缺失

## Migration Strategy

1. **安装新依赖**：添加 Tailwind CSS、Headless UI 等
2. **配置 Tailwind**：创建 `tailwind.config.js` 和主题配置
3. **删除旧代码**：移除 `frontend/src/views/` 下所有现有页面
4. **实现后端 API**：优先实现认证 API 和 RPA 服务层
5. **实现前端组件**：从 Landing Page 开始，逐步添加组件
6. **集成 WebSocket**：实现实时状态推送
7. **测试登录流程**：端到端测试用户辅助登录

## Success Criteria

- [ ] 前端只有 2 个视图：Landing Page 和 Authenticated Page
- [ ] 使用 #5C6BC0 作为主色调
- [ ] 实现玻璃拟态视觉效果（背景模糊、半透明）
- [ ] 支持亮色/暗色主题切换
- [ ] 登录按钮点击后，RPA 能打开浏览器到 BOSS 直聘登录页
- [ ] 用户手动登录后，前端能实时显示账号信息
- [ ] WebSocket 连接稳定，状态更新延迟 < 500ms
- [ ] RPA 浏览器在 5 分钟未操作时自动关闭
- [ ] Cookie 正确保存到 SQLite，下次启动自动恢复会话
- [ ] 无 WebDriver 检测特征（通过 bot-detector 测试）
