# Design: BOSS Secure Login UI & Frontend Modernization

## Context

### Current State

**前端架构**：
- Vue 3 + TypeScript + Vite
- Element Plus UI 组件库（默认主题）
- Vue Router 多页面架构（jobs, tasks, accounts, settings）
- Pinia 状态管理（但未充分利用）
- SCSS 样式预处理器

**后端架构**：
- FastAPI + SQLite（从 MongoDB 迁移而来）
- DrissionPage RPA 框架
- RESTful API 设计
- 当前缺乏 WebSocket 支持

**问题分析**：
1. **过度设计**：简单的 RPA 工具使用了复杂的多页面架构
2. **视觉陈旧**：Element Plus 默认样式缺乏品牌识别度
3. **登录风险**：直接自动化操作容易被 BOSS 直聘检测封号
4. **状态盲区**：前端无法实时获取 RPA 操作状态

### Constraints

**技术约束**：
- 必须使用现有的 DrissionPage RPA 框架
- 后端必须保持 Python + FastAPI
- 数据库使用 SQLite（已迁移）
- 前端必须保持 Vue 3（TypeScript）

**安全约束**：
- 必须避免明显的自动化特征
- Cookie 存储需要加密
- WebSocket 连接需要认证
- 浏览器资源需要限制（内存、超时）

**设计约束**：
- 主色调 #5C6BC0（靛蓝色）
- 必须支持亮色/暗色主题
- 必须实现玻璃拟态效果
- 必须响应式设计（桌面 + 移动端）

**时间约束**：
- 需要快速完成重构（不需要备份旧代码）
- 优先实现核心功能（登录 + 状态显示）

### Stakeholders

**主要用户**：
- HR 招聘人员：需要简单易用的工具，不关心技术细节
- 系统管理员：需要监控 RPA 状态，管理会话

**技术团队**：
- 前端开发者：需要清晰的组件结构和样式系统
- 后端开发者：需要模块化的 RPA 服务层
- DevOps：需要可靠的部署和监控

## Goals / Non-Goals

### Goals

1. **极简单页应用**：只保留登录页面和已登录状态显示，删除其他页面
2. **现代化视觉设计**：玻璃拟态 + #5C6BC0 主色调 + 亮/暗主题
3. **安全辅助登录**：用户手动扫码登录，RPA 只负责启动浏览器和保存会话
4. **实时状态同步**：WebSocket 推送登录状态，延迟 < 500ms
5. **会话持久化**：Cookie 加密存储，自动恢复会话
6. **反自动化检测**：隐藏 WebDriver 特征，模拟真实浏览器

### Non-Goals

- ~~实现职位管理、任务管理等高级功能~~（暂时删除）
- ~~实现全自动登录（账号密码自动填写）~~（安全风险高）
- ~~实现多账号管理~~（本次只支持单账号）
- ~~实现复杂的权限系统~~（暂时不需要）
- ~~实现数据可视化仪表板~~（后续迭代）

## Decisions

### 1. UI 框架：Tailwind CSS + Headless UI vs Element Plus

**决策**：使用 Tailwind CSS + Headless UI

**理由**：
- ✅ **完全自定义样式**：Tailwind 可以精确实现玻璃拟态效果和 #5C6BC0 主题
- ✅ **包体积更小**：按需生成 CSS，相比 Element Plus 减少约 200KB
- ✅ **设计系统一致性**：通过 Tailwind 配置统一设计 token（颜色、间距、圆角）
- ✅ **现代化**：Headless UI 提供无样式组件，配合 Tailwind 实现完全定制

**替代方案考虑**：
- **Element Plus 自定义主题**：虽然可行，但仍然受限于组件结构，无法实现真正的玻璃拟态
- **Naive UI**：设计更现代，但组件样式仍然不够灵活

**权衡**：
- ⚠️ 学习成本：团队需要熟悉 Tailwind CSS 的 utility-first 理念
- ⚠️ 开发时间：需要从零构建组件，但可以通过模板加速

### 2. 状态管理：Pinia Centralized Store vs Composables

**决策**：Pinia Store + Composables 混合模式

**理由**：
- ✅ **集中式状态**：Pinia Store 管理全局状态（auth、theme、rpa）
- ✅ **可复用逻辑**：Composables 封装业务逻辑（useAuth、useRPA、useTheme）
- ✅ **DevTools 集成**：Pinia 支持时间旅行调试

**架构设计**：
```typescript
// Pinia Store（全局状态）
stores/
├── auth.ts      // { isAuthenticated, user, session }
├── theme.ts     // { mode: 'light' | 'dark', color: '#5C6BC0' }
└── rpa.ts       // { status: 'idle' | 'browser_open' | 'logged_in', browserId }

// Composables（业务逻辑）
composables/
├── useAuth.ts   // login(), logout(), checkStatus()
├── useRPA.ts    // startLogin(), monitorStatus()
└── useTheme.ts  // toggleTheme(), setTheme()
```

### 3. 实时通信：WebSocket (FastAPI Native) vs Polling

**决策**：使用 FastAPI 原生 WebSocket

**理由**：
- ✅ **低延迟**：实时推送，延迟 < 100ms（轮询需要 1-5s）
- ✅ **服务器效率**：避免频繁 HTTP 请求，减少 CPU 和网络开销
- ✅ **原生支持**：FastAPI 内置 WebSocket，无需额外依赖
- ✅ **双向通信**：前端可以发送心跳，服务器可以推送状态

**实现方案**：
```python
# 后端：WebSocket 连接管理器
@app.websocket("/ws/auth")
async def auth_websocket(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 等待前端心跳
            await websocket.receive_text()

            # 推送最新状态
            await manager.broadcast(await get_auth_status())
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

**权衡**：
- ⚠️ 长连接占用：每个客户端占用一个服务器连接（但用户量小，可接受）
- ⚠️ 重连逻辑：需要实现自动重连机制（前端使用 `socket.io-client` 或原生 `WebSocket`）

### 4. RPA 浏览器管理：Singleton Pattern vs Pool Pattern

**决策**：单例模式（Singleton）+ 超时清理

**理由**：
- ✅ **资源限制**：只允许一个浏览器实例（内存占用 200-500MB）
- ✅ **简化状态管理**：单账号场景下不需要并发
- ✅ **避免冲突**：多个浏览器实例可能导致 Cookie 冲突

**架构设计**：
```python
class BrowserManager:
    _instance = None
    _browser = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def start_browser(self):
        if self._browser:
            await self.close_browser()

        self._browser = Browser(
            configs=AntiDetection.get_config()
        )
        self._browser.get('https://login.zhipin.com/')

        # 启动超时计时器（5分钟）
        asyncio.create_task(self._timeout_check())

    async def _timeout_check(self):
        await asyncio.sleep(300)  # 5 分钟
        if not is_logged_in():
            await self.close_browser()
```

**替代方案考虑**：
- **对象池模式**：适合多账号场景，但增加复杂度

### 5. 反自动化检测：DrissionPage 配置 vs undetected-chromedriver

**决策**：使用 DrissionPage + 自定义反检测配置

**理由**：
- ✅ **现有框架**：已经在使用 DrissionPage，无需引入新依赖
- ✅ **配置灵活**：可以通过自定义配置隐藏自动化特征
- ✅ **稳定性好**：DrissionPage 基于 CDP（Chrome DevTools Protocol），更稳定

**反检测配置**：
```python
class AntiDetection:
    @staticmethod
    def get_config():
        return BrowserConfig(
            # 使用真实 Chrome User-Agent
            user_agent=random.choice([
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ...',
            ]),

            # 禁用 WebDriver 标志
            arguments=[
                '--disable-blink-features=AutomationControlled',
                '--exclude-switches=enable-automation',
                '--disable-infobars',
            ],

            # 注入 JavaScript 修改 navigator.webdriver
            js_code='''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
            ''',

            # 设置真实窗口大小（避免被检测为 headless）
            window_size=(1920, 1080),
            headless=False,  # 必须显示浏览器
        )
```

**权衡**：
- ⚠️ 无法完全隐藏：BOSS 直聘可能使用高级检测（Canvas 指纹、行为分析）
- ⚠️ 需要持续更新：反检测配置需要根据 BOSS 的检测策略调整

### 6. 会话存储：加密 Cookie vs Access Token

**决策**：加密存储 Cookie + SQLite 持久化

**理由**：
- ✅ **简单可靠**：BOSS 直聘使用 Cookie 认证，直接存储即可
- ✅ **自动续期**：Cookie 不会过期（除非用户退出）
- ✅ **减少依赖**：无需实现 OAuth 或 JWT 体系

**加密方案**：
```python
from cryptography.fernet import Fernet

class SessionManager:
    def __init__(self):
        self.cipher = Fernet(generate_key())

    def save_session(self, cookies: List[Dict]):
        encrypted = self.cipher.encrypt(
            json.dumps(cookies).encode()
        )

        db.execute(
            'INSERT INTO sessions (cookies, user_info) VALUES (?, ?)',
            [encrypted, extract_user_info(cookies)]
        )

    def load_session(self):
        row = db.execute('SELECT cookies FROM sessions ORDER BY created_at DESC LIMIT 1')
        decrypted = self.cipher.decrypt(row[0])
        return json.loads(decrypted)
```

**安全性**：
- ✅ 加密密钥存储在环境变量（`.env`）
- ✅ SQLite 数据库文件权限限制
- ⚠️ 仍然需要物理服务器安全（防止数据库文件被复制）

### 7. 主题系统：CSS Variables vs Tailwind darkMode

**决策**：Tailwind `darkMode: 'class'` + CSS Variables

**理由**：
- ✅ **Tailwind 原生支持**：通过 `dark:` 前缀实现暗色模式
- ✅ **CSS Variables 动态化**：可以通过 JS 动态修改颜色（#5C6BC0）
- ✅ **自动跟随系统**：使用 `prefers-color-scheme` 媒体查询

**实现方案**：
```css
/* styles/theme.css */
:root {
  --primary: #5C6BC0;
  --primary-light: #7E8CD8;
  --primary-dark: #3F51B5;
  --glass-bg: rgba(255, 255, 255, 0.7);
  --glass-border: rgba(255, 255, 255, 0.18);
}

.dark {
  --primary: #7E8CD8;
  --glass-bg: rgba(0, 0, 0, 0.7);
  --glass-border: rgba(255, 255, 255, 0.08);
}
```

```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        primary: 'var(--primary)',
        'primary-light': 'var(--primary-light)',
        glass: 'var(--glass-bg)',
      },
      backdropBlur: {
        glass: '20px',
      },
    },
  },
}
```

### 8. 前端路由：Single Page vs Multi-Page

**决策**：单页应用（无路由或最小路由）

**理由**：
- ✅ **极简体验**：所有功能在一个页面，无需路由切换
- ✅ **减少复杂度**：不需要管理路由守卫、页面状态
- ✅ **快速加载**：首屏加载后无额外网络请求

**架构设计**：
```typescript
// App.vue（无路由）
<template>
  <div class="app" :class="{ dark: isDark }">
    <LandingPage v-if="!isAuthenticated" />
    <AuthenticatedPage v-else />
  </div>
</template>

// 或者最小路由（如果未来需要扩展）
const routes = [
  { path: '/', component: LandingPage },
  { path: '/dashboard', component: AuthenticatedPage, meta: { requiresAuth: true } }
]
```

## Risks / Trade-offs

### Risk 1: RPA 浏览器资源泄漏

**描述**：浏览器实例未正确关闭，导致内存泄漏（200-500MB/实例）

**缓解措施**：
- ✅ 实现 5 分钟超时自动关闭
- ✅ 使用 Python `asyncio` 任务管理，确保进程退出时清理
- ✅ 添加健康检查 API（`/api/health`），监控内存占用
- ✅ 限制同时只能有一个浏览器实例（单例模式）

### Risk 2: WebSocket 连接断开

**描述**：网络波动或服务器重启导致 WebSocket 断开，前端状态不同步

**缓解措施**：
- ✅ 前端实现自动重连机制（指数退避：1s, 2s, 4s, 8s, ...）
- ✅ 定期发送心跳（每 30s），检测连接状态
- ✅ 断线重连后自动调用 `/api/auth/status` 恢复状态
- ✅ UI 显示连接状态指示器（绿色=已连接，红色=断开）

### Risk 3: BOSS 直聘检测升级

**描述**：BOSS 直聘升级反爬策略，导致 RPA 浏览器被识别并封号

**缓解措施**：
- ✅ 用户辅助登录（用户手动扫码），避免自动化操作
- ✅ 隐藏 WebDriver 特征（`navigator.webdriver = undefined`）
- ✅ 使用真实 User-Agent 和浏览器配置
- ⚠️ **无法完全避免**：如果 BOSS 使用 Canvas 指纹或行为分析，仍然可能被检测
- 🔄 **持续更新**：需要根据 BOSS 的检测策略调整反检测配置

### Risk 4: Cookie 加密密钥泄露

**描述**：加密密钥被泄露，导致 Cookie 被解密，账号被盗用

**缓解措施**：
- ✅ 密钥存储在环境变量（`.env`），不提交到 Git
- ✅ 生产环境使用密钥管理服务（AWS Secrets Manager / HashiCorp Vault）
- ✅ 数据库文件权限限制（`chmod 600`）
- ⚠️ **仍然有风险**：如果服务器被入侵，环境变量仍然可以被读取
- 🔄 **未来改进**：考虑使用硬件安全模块（HSM）或密钥轮换机制

### Risk 5: Tailwind CSS 样式冲突

**描述**：Tailwind 的 utility class 与现有样式冲突，导致 UI 异常

**缓解措施**：
- ✅ 完全删除旧代码（不需要备份），避免冲突
- ✅ 使用 Tailwind 的 `@apply` 指令封装常用样式
- ✅ 配置 `tailwind.config.js` 的 `prefix` 选项（如果需要与第三方库共存）
- ✅ 使用 `!important` 覆盖第三方库样式（如 Headless UI 的默认样式）

### Risk 6: 暗色模式视觉一致性问题

**描述**：玻璃拟态效果在暗色模式下可读性差，或颜色对比度不足

**缓解措施**：
- ✅ 使用 CSS Variables 定义主题颜色，暗色模式使用不同的值
- ✅ 调整玻璃拟态参数（暗色模式：`rgba(0,0,0,0.7)`，亮色模式：`rgba(255,255,255,0.7)`）
- ✅ 使用 WCAG 标准检查对比度（至少 4.5:1）
- ✅ 在主流浏览器和设备上测试（Chrome, Safari, Firefox）

### Risk 7: WebSocket 性能瓶颈

**描述**：大量并发连接导致服务器资源耗尽（CPU、内存、文件描述符）

**缓解措施**：
- ✅ 当前用户量小（< 10），不太可能出现瓶颈
- ✅ 使用异步 FastAPI，单个连接占用内存 < 10KB
- ✅ 设置连接超时（5 分钟无活动自动断开）
- 🔄 **未来扩展**：如果用户量增长，考虑使用 Redis Pub/Sub 或消息队列

### Risk 8: RPA 浏览器启动慢

**描述**：浏览器启动需要 3-5 秒，用户可能以为系统无响应

**缓解措施**：
- ✅ 显示加载动画（Spinner）和进度提示（"正在启动浏览器..."）
- ✅ WebSocket 实时推送状态变化（`browser_starting` → `browser_ready` → `waiting_login`）
- ✅ 优化浏览器启动参数（禁用不必要的扩展、GPU 加速）
- ⚠️ **无法完全消除**：浏览器冷启动需要时间

## Migration Plan

### 部署步骤

**阶段 1：依赖安装和配置（Day 1）**
1. 安装前端依赖：`npm install -D tailwindcss @headlessui/vue @vueuse/core`
2. 配置 Tailwind CSS：创建 `tailwind.config.js` 和 `styles/theme.css`
3. 安装后端依赖：无（使用现有 DrissionPage 和 FastAPI）

**阶段 2：删除旧代码（Day 1）**
1. 删除 `frontend/src/views/` 下所有文件
2. 删除 `frontend/src/api/account.ts`、`job.ts`、`task.ts`（暂时不需要）
3. 从 `frontend/package.json` 移除 `element-plus` 和 `@element-plus/icons-vue`

**阶段 3：后端实现（Day 2）**
1. 创建 `backend/app/services/rpa_service.py`（RPA 服务层）
2. 创建 `backend/rpa/modules/browser_manager.py`（浏览器管理）
3. 创建 `backend/rpa/modules/anti_detection.py`（反检测配置）
4. 创建 `backend/app/api/auth.py`（认证 API）
5. 更新 `backend/app/main.py`（添加 WebSocket 路由）
6. 运行数据库迁移：创建 `sessions` 和 `login_logs` 表

**阶段 4：前端实现（Day 3）**
1. 创建 `frontend/src/stores/auth.ts`（Pinia Store）
2. 创建 `frontend/src/composables/useAuth.ts`、`useRPA.ts`、`useTheme.ts`
3. 创建 `frontend/src/components/LandingPage.vue`（首页/登录页）
4. 创建 `frontend/src/components/AuthenticatedPage.vue`（已登录状态显示）
5. 创建 `frontend/src/components/StatusIndicator.vue`（连接状态指示器）
6. 创建 `frontend/src/components/LoginButton.vue`（登录按钮）
7. 创建 `frontend/src/components/AccountCard.vue`（账号信息卡片）
8. 更新 `frontend/src/App.vue` 和 `frontend/src/router/index.ts`

**阶段 5：集成和测试（Day 4）**
1. 集成 WebSocket：前端连接 `/ws/auth`，后端推送状态
2. 测试登录流程：点击登录 → 浏览器打开 → 扫码登录 → 状态更新
3. 测试会话恢复：重启后端 → 前端自动恢复登录状态
4. 测试暗色模式：切换主题，检查所有组件的视觉效果
5. 测试响应式：在桌面和移动端检查布局

**阶段 6：部署和监控（Day 5）**
1. 构建前端：`cd frontend && npm run build`
2. 启动后端：`cd backend && python -m app.main`
3. 监控日志：检查 RPA 浏览器启动、WebSocket 连接、错误日志
4. 性能测试：使用 Lighthouse 检查前端性能（目标 > 90 分）

### 回滚策略

**如果出现严重问题**：
1. **保留旧代码的 Git commit**：可以通过 `git reset --hard <commit>` 回滚
2. **数据库迁移可逆**：`sessions` 和 `login_logs` 表不影响现有功能
3. **前端独立回滚**：如果前端有问题，可以只回滚 `frontend/` 目录
4. **后端独立回滚**：如果后端有问题，可以只回滚 `backend/` 目录

**回滚步骤**：
```bash
# 查看提交历史
git log --oneline

# 回滚到重构前的 commit
git reset --hard <commit-id>

# 重新安装依赖
cd frontend && npm install
cd backend && pip install -r requirements.txt

# 重启服务
python backend/app/main.py
```

## Open Questions

### Q1: RPA 浏览器是否需要无头模式（Headless）？

**背景**：无头模式可以节省资源（约 30% 内存），但更容易被检测。

**当前倾向**：显示浏览器（`headless=False`），因为：
- 用户辅助登录需要看到扫码页面
- 无头模式更容易被检测（Canvas 指纹、窗口大小特征）

**需要验证**：测试 DrissionPage 在无头模式下的检测率

### Q2: WebSocket 认证机制如何实现？

**背景**：WebSocket 连接需要认证，避免未授权访问。

**当前倾向**：使用查询参数传递 Token：
```
ws://localhost:8000/ws/auth?token=xxx
```

**需要决策**：Token 有效期、刷新机制、存储方式（localStorage vs Cookie）

### Q3: Cookie 加密算法选择？

**背景**：需要选择对称加密算法（AES vs Fernet vs ChaCha20）

**当前倾向**：使用 `cryptography.fernet`（基于 AES-128-CBC），因为：
- API 简单易用
- 自动处理密钥派生和 HMAC
- 性能足够（Cookie 数据量小）

**需要验证**：性能测试（如果频繁加解密）

### Q4: 玻璃拟态效果的浏览器兼容性？

**背景**：玻璃拟态需要 `backdrop-filter: blur()`，旧浏览器不支持。

**当前倾向**：使用渐进增强：
```css
.glass {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}

@supports not (backdrop-filter: blur(20px)) {
  .glass {
    background: rgba(255, 255, 255, 0.95);
  }
}
```

**需要验证**：在 IE11、旧版 Safari 上的降级效果

### Q5: 是否需要实现"记住登录状态"功能？

**背景**：用户关闭浏览器后，下次打开是否自动登录。

**当前倾向**：自动恢复会话（从 SQLite 加载 Cookie），因为：
- 用户体验更好（无需频繁登录）
- Cookie 已加密存储，安全性可接受
- BOSS 直聘的 Cookie 有效期较长（约 30 天）

**需要决策**：是否添加"自动登录"开关（让用户选择）

### Q6: RPA 浏览器超时时间设置？

**背景**：当前设置为 5 分钟，但可能不够灵活。

**当前倾向**：固定 5 分钟，因为：
- 用户扫码登录通常在 1 分钟内完成
- 5 分钟足够处理各种异常情况
- 简化实现（不需要配置系统）

**需要验证**：实际用户测试，收集登录时间数据

### Q7: 是否需要实现多语言支持？

**背景**：当前只支持中文，未来可能需要英文。

**当前倾向**：暂不支持，因为：
- 目标用户是 HR 招聘人员（中文）
- 增加复杂度（需要 i18n 框架）
- 可以后续迭代添加

**需要决策**：是否预留 i18n 接口（使用 Vue I18n）

## Appendix

### A. 技术栈总览

**前端**：
- Vue 3.4+（Composition API）
- TypeScript 5.0+
- Vite 5.0+
- Tailwind CSS 3.4+
- Headless UI Vue
- Pinia 2.1+
- VueUse 10.0+
- WebSocket API（原生或 socket.io-client）

**后端**：
- Python 3.9+
- FastAPI 0.104+
- DrissionPage 4.0+
- SQLite 3（aiosqlite）
- WebSocket（FastAPI 原生）
- Cryptography（Fernet 加密）

**开发工具**：
- ESLint + Prettier（前端）
- Ruff + Black（后端）
- Pytest（测试）
- Git Hooks（pre-commit）

### B. 参考资源

**设计参考**：
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Headless UI Vue](https://headlessui.com/vue)
- [Glassmorphism CSS Generator](https://ui.glass/generator)
- [Material Design 3 - Color System](https://m3.material.io/styles/color/the-color-system/tokens)

**技术参考**：
- [DrissionPage Documentation](https://drissionpage.cn/)
- [FastAPI WebSocket](https://fastapi.tiangolo.com/advanced/websockets/)
- [Pinia Getting Started](https://pinia.vuejs.org/getting-started.html)
- [VueUse Core](https://vueuse.org/)

**安全参考**：
- [OWASP Automated Threats to Web Applications](https://owasp.org/www-project-automated-threats-to-web-applications/)
- [Anti-Web Scraping Techniques](https://www.zenrows.com/blog/prevent-web-scraping)
- [Bot Detection - How to Bypass](https://stackoverflow.com/questions/59080669/how-to-bypass-bot-detection)
