# RPA_BOSS 项目开发指南

## 项目架构速记

### 前端架构
- **路由模式**: Vue Router 4 真正的页面级路由（非条件渲染）
- **登录页**: `/login` → `LoginView.vue` → `LandingPage.vue`（仅登录表单）
- **主应用**: `/` → `MainLayout.vue` → 4个标签页

### 重要原则

#### ❌ 错误模式：条件渲染替代路由跳转

```vue
<!-- 错误示例 -->
<template>
  <LandingPage v-if="!isAuthenticated" />
  <AuthenticatedPage v-else />
</template>
```

**问题**：
- 用户停留在同一 URL (`/login`)，只是内容切换
- 路由守卫不会触发（因为没有路由变化）
- 用户刷新页面可能回到登录页

#### ✅ 正确模式：使用路由系统

```vue
<!-- LoginView.vue - 只显示登录页 -->
<template>
  <LandingPage />
</template>

<script setup>
onMounted(() => {
  // 已登录则跳转
  if (authStore.isAuthenticated) {
    router.push('/')
  }
})
</script>
```

```vue
<!-- App.vue - 监听认证状态，自动跳转 -->
<script setup>
watch(() => authStore.isAuthenticated, (isAuthenticated) => {
  if (isAuthenticated && router.currentRoute.value.path === '/login') {
    router.push('/')
  }
})
</script>
```

---

## 刚刚修复的错误：登录后不跳转

### 错误现象
用户扫码登录成功后，前端停留在登录页面，没有跳转到主页。

### 根本原因

1. **LoginView.vue 使用了条件渲染**
   - `v-if="!isAuthenticated"` vs `v-else`
   - 导致用户永远停留在 `/login` 路由

2. **缺少主动路由跳转**
   - `authStore.setAuth()` 只更新状态
   - 没有 `router.push('/')` 触发页面跳转

3. **路由守卫未触发**
   - 守卫只在**路由变化时**触发
   - 条件渲染不产生路由变化，守卫永远不会执行

### 修复方案

**文件**: `frontend/src/views/LoginView.vue`
```vue
<template>
  <!-- 只显示登录页面，不要条件渲染 -->
  <LandingPage />
</template>

<script setup>
onMounted(() => {
  // 已登录则跳转
  if (authStore.isAuthenticated) {
    router.push('/')
  }
})
</script>
```

**文件**: `frontend/src/App.vue`
```vue
<script setup>
// 监听认证状态变化
watch(() => authStore.isAuthenticated, (isAuthenticated) => {
  if (isAuthenticated && router.currentRoute.value.path === '/login') {
    router.push('/')  // 登录成功后跳转
  }
})
</script>
```

---

## 通用编码原则

### 1. 路由 vs 条件渲染

| 场景 | 使用方式 | 不使用方式 |
|------|----------|------------|
| 页面级导航 | `router.push()`, 路由守卫 | 条件渲染整个页面 |
| 组件级切换 | `v-if`, `v-show`, 动态组件 | 路由跳转 |

### 2. Pinia Store 限制

**不能在 Store 中直接使用**：
- ❌ `useRouter()`, `useRoute()`
- ❌ 任何 Vue Composition API 的 hook（需要在 setup 上下文中）

**替代方案**：
- ✅ 在组件中监听 store 状态，执行跳转
- ✅ 在 `App.vue` 中添加全局监听器

### 3. 数据库初始化顺序

**错误模式**：
```python
await db.connect()  # 创建了数据库文件！
await init_database()  # 检查文件是否存在，存在就跳过创建！
```

**正确模式**：
```python
# 方案1: init_database 总是执行 CREATE TABLE IF NOT EXISTS
async def init_database():
    await create_schema()  # 总是调用，使用 IF NOT EXISTS

# 方案2: 检查表是否存在而不是文件
async def init_database():
    conn = await db.get_connection()
    cursor = await conn.execute(
        "SELECT name FROM sqlite_master WHERE name='accounts'"
    )
    if not await cursor.fetchone():
        await create_schema()
```

---

## 文件速查表

### 前端核心文件

| 文件 | 用途 | 注意事项 |
|------|------|----------|
| `src/App.vue` | 根组件，路由出口 | 添加全局状态监听 |
| `src/router/index.ts` | 路由配置和守卫 | 保护需要认证的页面 |
| `src/stores/auth.ts` | 认证状态管理 | 不要在这里调用 useRouter |
| `src/views/LoginView.vue` | 登录页 | 只显示登录表单，不要条件渲染 |
| `src/layouts/MainLayout.vue` | 主布局（带侧边栏） | `/` 路由的入口 |

### 后端核心文件

| 文件 | 用途 | 注意事项 |
|------|------|----------|
| `app/main.py` | FastAPI 应用入口 | lifespan 中按正确顺序初始化 |
| `app/core/database.py` | 数据库连接 | `init_database()` 要确保表被创建 |
| `app/api/auth.py` | 认证 API | WebSocket 状态广播 |

---

## 常见错误模式

### 1. try-except 缺少 except/finally

```python
# ❌ 错误
try:
    loop.run_until_complete(...)

if existing_session:  # 缩进错误，不在 try 块内
    pass

# ✅ 正确
loop.run_until_complete(...)

if existing_session:
    pass
```

### 2. computed 中访问 ref 需要 .value

```typescript
// ❌ 错误
const isDark = computed(() => mode === 'dark')  // mode 是 Ref

// ✅ 正确
const isDark = computed(() => mode.value === 'dark')  // mode.value 是实际值
```

### 3. Pinia store 返回 Ref 需要正确处理

```typescript
// useTheme 返回 { mode: themeStore.mode }
// mode 是 Ref<string>，不是 string

// ❌ 错误
const isDark = computed(() => mode === 'dark')

// ✅ 正确
const isDark = computed(() => mode.value === 'dark')
// 或者
const isDark = computed(() => {
  const themeStore = useThemeStore()
  return themeStore.mode === 'dark'
})
```

---

## 修改代码前必读

### 修改 Store 时
1. 检查是否需要调用路由 → 在组件中添加 watch，不要在 Store 中调用
2. 检查是否有异步操作 → 标记为 async 函数
3. 检查是否需要持久化 → 使用 localStorage

### 修改路由时
1. 检查路由守卫是否会冲突
2. 检查 meta 字段是否正确设置 (`requiresAuth`)
3. 确保嵌套路由的父组件使用 `<RouterView>`

### 修改数据库时
1. `db.connect()` 会创建文件，`init_database()` 要检查表是否存在
2. 使用 `CREATE TABLE IF NOT EXISTS` 确保幂等性
3. 迁移文件按数字顺序执行

---

## 登录流程完整实现模式

### 问题：浏览器启动了但前端不跳转

**错误模式**：只调用 `start_login()` 没有后续监控

```python
# ❌ 错误
@router.post("/login")
async def login(request: LoginRequest):
    result = await rpa_service.start_login()
    return result  # 返回后就结束了，没有监控扫码
```

**正确模式**：使用后台任务持续监控

```python
# ✅ 正确
from fastapi import BackgroundTasks

@router.post("/login")
async def login(request: LoginRequest, background_tasks: BackgroundTasks):
    result = await rpa_service.start_login()
    if result["status"] == "browser_opened":
        # 启动后台监控任务，不会阻塞响应
        background_tasks.add_task(monitor_and_broadcast_login)
    return result

async def monitor_and_broadcast_login():
    """后台任务：监控登录并广播结果"""
    result = await rpa_service.monitor_login()
    if result["status"] == "success":
        await broadcast_status(await rpa_service.get_status())
```

### 问题：WebSocket 消息处理为空操作

**错误模式**：

```typescript
// ❌ 错误 - 收到消息不处理
case 'status_update':
  break  // 什么都不做！
```

**正确模式**：

```typescript
// ✅ 正确 - 更新认证状态
case 'status_update':
  if (data.data?.is_logged_in) {
    const authStore = useAuthStore()
    authStore.setAuth({
      isAuthenticated: true,
      user: data.data.user_info
    })
  }
  break
```

### 问题：只依赖 WebSocket 没有备选方案

**错误模式**：WebSocket 断开就无法检测登录

**正确模式**：同时使用 WebSocket 和轮询（双重保障）

```typescript
// ✅ 双重保障
async function handleLogin() {
  await login()
  // 启动轮询作为备选
  startPollingLoginStatus((isLogged) => {
    if (isLogged) {
      // 登录成功处理
    }
  })
}
```

### 问题：异常处理返回 None 导致 ChromiumPage 初始化失败

**错误模式**：

```python
# ❌ 错误
except Exception:
    return None  # ChromiumPage(addr_or_opts=None) 可能失败
```

**正确模式**：

```python
# ✅ 正确
except Exception:
    return {}  # 空字典，DrissionPage 使用默认配置
```

---

## 登录流程调试清单

当登录功能出现问题时，按以下顺序检查：

1. **后端检查**：
   - [ ] Chrome 是否安装在标准路径
   - [ ] DrissionPage 是否正确安装 (`python -c "import DrissionPage"`)
   - [ ] `/api/auth/login` 是否返回 `{"status": "browser_opened"}`
   - [ ] 后台监控任务是否启动 (查看日志 "Background login monitoring task started")
   - [ ] `monitor_login()` 是否在后台运行

2. **前端检查**：
   - [ ] WebSocket 是否连接 (查看 "WebSocket connected" 日志)
   - [ ] `status_update` 消息是否被正确处理
   - [ ] 轮询是否启动 (查看 "Starting login status polling..." 日志)
   - [ ] `authStore.isAuthenticated` 是否被更新
   - [ ] `App.vue` 的 watch 是否触发路由跳转

3. **浏览器检查**：
   - [ ] 浏览器窗口是否打开
   - [ ] 是否导航到 `https://login.zhipin.com/`
   - [ ] 扫码后 URL 是否变化 (不再包含 "login.zhipin.com")

---

## 修改的文件清单（本次修复）

### 后端文件
1. `backend/app/api/auth.py` - 添加后台监控任务
2. `backend/rpa/modules/browser_manager.py` - 添加详细日志
3. `backend/rpa/modules/anti_detection.py` - 修复异常处理

### 前端文件
1. `frontend/src/composables/useWebSocket.ts` - 修复 status_update 处理
2. `frontend/src/composables/useAuth.ts` - 添加轮询功能
3. `frontend/src/components/LandingPage.vue` - 添加状态监听和轮询

---

## 2025-03-03 主页启动架构重构

### 需求变更
- 应用启动后直接进入主页（无需先登录）
- 在主页添加"启动BOSS网页"按钮
- 点击按钮后打开浏览器，用户扫码登录
- 强化反检测措施防止账号被封

### 修改的文件

#### 前端
1. `frontend/src/router/index.ts` - 移除强制登录检查
2. `frontend/src/views/HomeView.vue` - 添加未登录状态UI和启动按钮
3. `frontend/src/composables/useBrowserLaunch.ts` - 新建浏览器启动逻辑封装

#### 后端
1. `backend/rpa/modules/anti_detection.py` - 添加 JavaScript 注入方法
2. `backend/rpa/modules/browser_manager.py` - 启动时注入反检测脚本
3. `backend/app/services/rpa_service.py` - 登录流程中再次注入脚本

### 本次修改中避免的错误

#### 1. TypeScript 导入路径错误
```typescript
// ❌ 错误 - @/utils/api 不存在
import api from '@/utils/api'

// ✅ 正确 - API 在 @/api 目录
import api from '@/api'
```

#### 2. 未使用的导入导致编译错误
```typescript
// ❌ 错误 - useAuthStore 导入但未使用
import { useAuthStore } from '@/stores/auth'

export function useBrowserLaunch() {
  const authStore = useAuthStore()  // 未使用
  // ...
}

// ✅ 正确 - 移除未使用的导入
export function useBrowserLaunch() {
  const rpaStore = useRPAStore()
  // ...
}
```

#### 3. 路由守卫修改导致访问控制变化
```typescript
// ❌ 原来的方式 - 未登录被强制跳转登录页
router.beforeEach((to, _from, next) => {
  const requiresAuth = to.meta.requiresAuth !== false
  if (requiresAuth && !isAuthenticated) {
    next({ name: ROUTE_NAMES.Login })
  }
  // ...
})

// ✅ 新方式 - 允许未登录访问主页
router.beforeEach((to, _from, next) => {
  // 只在显式访问 /login 时重定向到首页
  if (to.name === ROUTE_NAMES.Login) {
    next({ name: ROUTE_NAMES.Home })
  } else {
    next()
  }
})
```

### 反检测增强要点

#### JavaScript 注入时机
1. **浏览器启动时**：`BrowserManager.start_browser()` 立即注入
2. **页面导航后**：`RPAService.start_login()` 导航到登录页后再次注入

#### 注入的反检测脚本
```javascript
// 最关键 - 隐藏 webdriver 标识
Object.defineProperty(navigator, 'webdriver', {
  get: () => undefined
});

// 添加 window.chrome 对象
window.chrome = { runtime: {}, loadTimes: function() {}, ... };

// 模拟插件列表
Object.defineProperty(navigator, 'plugins', {
  get: () => [
    { name: 'Chrome PDF Plugin', ... },
    { name: 'Chrome PDF Viewer', ... }
  ]
});
```

#### 浏览器启动参数增强
```python
# 新增参数
options.set_argument("--disable-features=IsolateOrigins,site-per-process")
options.set_argument("--lang=zh-CN")
options.set_argument("--timezone=Asia/Shanghai")
options.set_argument("--window-position=100,100")  # 随机偏移
```

### 测试验证清单

#### 功能测试
- [ ] 未登录打开应用 → 直接进入主页
- [ ] 主页显示"启动BOSS网页"按钮
- [ ] 点击按钮 → 浏览器打开并导航到登录页
- [ ] 扫码登录 → 界面更新为已登录状态

#### 反检测验证
在浏览器控制台执行：
```javascript
// 应该返回 undefined
console.log(navigator.webdriver)

// 应该返回对象
console.log(window.chrome)

// 应该返回 > 0
console.log(navigator.plugins.length)
```

---

## 2025-03-03 Vue 模板结构错误：v-if/v-else 缩进问题

### 错误现象
```
[plugin:vite:vue] Element is missing end tag.
HomeView.vue:2:3
```

### 根本原因

**`v-else` 块的子元素缩进不对，导致它们成了 `v-else` 的兄弟元素而不是子元素。**

#### ❌ 错误代码结构

```vue
<template>
  <div class="space-y-6">
    <!-- 未登录状态 -->
    <div v-if="!isAuthenticated">...</div>

    <!-- 已登录状态 -->
    <div v-else>
      <div class="flex items-center justify-between">
        ...
      </div>  <!-- Welcome Section 结束 -->

    <!-- Statistics Cards -->  <!-- 缩进和上面一致！成了 v-else 的兄弟！ -->
    <div class="grid grid-cols-1...">
      ...
    </div>

    <!-- 更多内容... -->
  </div>  <!-- 外层 div 结束 -->
</template>
```

**问题**：
1. 第56行 Welcome Section 的 `</div>` 关闭后
2. 第59行 Statistics Cards 的缩进和第56行**对齐**
3. 这导致 Statistics Cards 成了 `v-else` 的**兄弟元素**，而不是子元素
4. `<div v-else>` 在第56行后就"隐式结束"了（实际上没有结束标签）
5. 第59行之后的内容都在 `v-else` 外面，破坏了模板结构

#### ✅ 正确代码结构

```vue
<template>
  <div class="space-y-6">
    <!-- 未登录状态 -->
    <div v-if="!isAuthenticated">...</div>

    <!-- 已登录状态 -->
    <div v-else>
      <div class="flex items-center justify-between">
        ...
      </div>

      <!-- Statistics Cards -->  <!-- 比 v-else 多缩进一层 -->
      <div class="grid grid-cols-1...">
        ...
      </div>

      <!-- Quick Actions -->  <!-- 同样多缩进一层 -->
      <div class="grid grid-cols-1...">
        ...
      </div>

      <!-- 所有已登录状态的内容都要在 v-else 内部 -->
    </div>  <!-- v-else 的结束标签 -->
  </div>
</template>
```

### 避免此错误的规则

#### 1. v-if/v-else 的子元素必须多缩进一层

```vue
<!-- ✅ 正确 -->
<div v-if="condition">
  <div>子元素</div>
  <div>另一个子元素</div>
</div>

<!-- ❌ 错误 -->
<div v-if="condition">
  <div>子元素</div>
<div>缩进不对，成了兄弟元素</div>
</div>
```

#### 2. 检查模板结构的缩进层级

在编写 Vue 模板时，确保：
- 每个 `<div>` 的开始和结束标签缩进一致
- 子元素比父元素多缩进一层（通常是 2 空格）
- `v-else` 块内的所有内容都要在 `v-else` 标签的缩进基础上再缩进

#### 3. 使用 IDE 的缩进辅助

- VSCode: 使用 `Format Document` (Shift+Alt+F)
- WebStorm: 使用 `Reformat Code` (Ctrl+Alt+L)
- 确保 Vue 文件使用 2 空格缩进

### 调试技巧

当遇到 "Element is missing end tag" 错误时：

1. **找到报错的行号**（如第2行）
2. **从报错行开始，检查每个 `<div>` 是否有对应的 `</div>`**
3. **特别关注 v-if/v-else 的结构**，确保子元素缩进正确
4. **使用代码编辑器的括号匹配功能**，点击开始标签看结束标签在哪里

### 快速检查清单

```vue
<!-- 检查这个结构是否正确 -->
<div v-if="!isAuthenticated">              <!-- 第1层 -->
  <GlassCard>                              <!-- 第2层 -->
    <h2>标题</h2>                          <!-- 第3层 -->
    <button>按钮</button>                  <!-- 第3层 -->
  </GlassCard>                             <!-- 第2层结束 -->
</div>                                     <!-- 第1层结束 -->

<div v-else>                               <!-- 第1层 -->
  <div class="flex">                       <!-- 第2层 -->
    <h1>欢迎</h1>                          <!-- 第3层 -->
  </div>                                   <!-- 第2层结束 -->

  <div class="grid">                       <!-- 第2层 - 必须和上面的 flex 同级 -->
    <GlassCard>内容</GlassCard>            <!-- 第3层 -->
  </div>                                   <!-- 第2层结束 -->
</div>                                     <!-- 第1层结束 -->
```

**关键**：第2层的所有开始标签必须缩进相同，它们的子元素（第3层）再多缩进一层。

---

## 2026-03-04 登录状态判断的正确模式

### 错误现象

点击"启动BOSS网页"按钮后出现"网络错误，请重试"，但几秒后界面错误地切换到已登录状态，实际上浏览器并未启动。

### 根本原因

1. **数据库中存在无效session** - 有cookies但user_info为空
2. **后端判断逻辑缺陷** - `is_logged_in`只检查session是否存在，不验证user_info
3. **前端盲目信任后端** - 直接使用`is_logged_in`值，不验证user_info是否存在

### ❌ 错误模式：只检查session是否存在

```python
# 后端 rpa_service.py
# ❌ 错误 - session存在但user_info可能为空
is_logged_in = session is not None
```

```typescript
// 前端 useWebSocket.ts
// ❌ 错误 - 直接使用is_logged_in
if (data.data?.is_logged_in) {
  authStore.setAuth({ isAuthenticated: true })
}
```

```typescript
// 前端 auth.ts
// ❌ 错误 - isAuthenticated为true就持久化
if (authData.isAuthenticated) {
  localStorage.setItem('auth', ...)
}
```

### ✅ 正确模式：同时检查session和user_info

```python
# 后端 rpa_service.py
# ✅ 正确 - session和user_info都必须存在
user_info = session.get("user_info") if session else None
is_logged_in = session is not None and user_info is not None and bool(user_info)
```

```python
# 后端 session_manager.py - load_session方法
# ✅ 正确 - 如果user_info无效，返回None
user_info = json.loads(user_info_json) if user_info_json else None

if not user_info or not user_info.get("username"):
    logger.warning("Session has no valid user_info, treating as invalid")
    await self.delete_session()
    return None
```

```typescript
// 前端 useWebSocket.ts
// ✅ 正确 - 同时验证user_info
const isLoggedIn = data.data?.is_logged_in
const userInfo = data.data?.user_info
const hasValidUserInfo = userInfo && Object.keys(userInfo).length > 0

if (isLoggedIn && hasValidUserInfo) {
  authStore.setAuth({ isAuthenticated: true, user: userInfo })
}
```

```typescript
// 前端 auth.ts - setAuth方法
// ✅ 正确 - 验证完整性后再设置状态
const isValidAuth = authData.isAuthenticated && authData.user && Object.keys(authData.user).length > 0

if (authData.isAuthenticated && !isValidAuth) {
  console.warn('setAuth called with isAuthenticated=true but no valid user info')
}

isAuthenticated.value = isValidAuth
user.value = isValidAuth ? authData.user : null

// 只持久化有效的认证状态
if (isValidAuth) {
  localStorage.setItem('auth', ...)
} else {
  localStorage.removeItem('auth')
}
```

```typescript
// 前端 auth.ts - loadFromStorage方法
// ✅ 正确 - 验证加载的数据完整性
const hasValidUser = data.user && Object.keys(data.user).length > 0

if (data.isAuthenticated && hasValidUser) {
  isAuthenticated.value = true
  user.value = data.user
} else {
  // 清除无效的存储数据
  localStorage.removeItem('auth')
}
```

### 修改的文件清单

| 文件 | 修改内容 |
|------|----------|
| `backend/rpa/modules/session_manager.py` | `load_session` 验证 user_info，无效则返回None |
| `backend/app/services/rpa_service.py` | `get_status` 双重验证 session 和 user_info |
| `frontend/src/stores/auth.ts` | `setAuth` 和 `loadFromStorage` 验证完整性 |
| `frontend/src/composables/useWebSocket.ts` | `status` 消息处理验证 user_info |

### 防御性编程原则

1. **后端**：不要只检查记录是否存在，要检查关键数据是否完整
2. **前端**：不要盲目信任后端返回的状态，要做二次验证
3. **持久化**：存储前验证数据完整性，加载时再次验证
4. **清理**：定期清理无效数据，避免脏数据影响判断

---

## 2026-03-04 前后端端口配置一致性

### 错误现象

点击"启动BOSS网页"按钮后出现"网络错误，请重试"提示，浏览器没有启动。

### 根本原因

**前端 API baseURL 配置的端口与后端实际运行端口不一致**

| 配置位置 | 错误值 | 正确值 |
|----------|--------|--------|
| `frontend/.env.development` | `localhost:3000` | `localhost:8000` |
| `frontend/vite.config.ts` | `localhost:8000` | ✅ 正确 |
| `backend/app/core/config.py` | `PORT: 8000` | ✅ 正确 |

### 问题链路

1. 用户点击按钮 → 前端调用 `api.post('/api/auth/login')`
2. Axios 使用 `baseURL = http://localhost:3000`
3. 请求发送到 `http://localhost:3000/api/auth/login`
4. 端口 3000 没有服务运行 → 请求失败
5. 捕获错误显示"网络错误，请重试"

### 检查清单：修改端口配置时必须同时检查

| 文件 | 配置项 | 说明 |
|------|--------|------|
| `frontend/.env.development` | `VITE_API_BASE_URL` | 前端 API 基础地址 |
| `frontend/vite.config.ts` | `server.proxy['/api'].target` | Vite 开发服务器代理目标 |
| `backend/app/core/config.py` | `PORT` | 后端实际运行端口 |

### 正确配置示例

```bash
# frontend/.env.development
VITE_API_BASE_URL=http://localhost:8000
```

```typescript
// frontend/vite.config.ts
server: {
  port: 5678,  // 前端开发服务器端口（可以不同）
  proxy: {
    '/api': {
      target: 'http://localhost:8000',  // 必须与后端端口一致
      changeOrigin: true,
    }
  }
}
```

```python
# backend/app/core/config.py
PORT: int = 8000  # 后端实际端口
```

### 注意事项

1. **axios baseURL 会绕过 Vite 代理**
   - 如果 axios 配置了 `baseURL: 'http://localhost:xxx'`
   - 请求会直接发到该地址，不走 Vite 代理
   - Vite 代理只在浏览器直接请求相对路径时生效

2. **保持三个端口配置一致**
   - `.env.development` 的端口 = 后端实际端口
   - `vite.config.ts` 代理目标 = 后端实际端口
   - `config.py` 的 PORT = 后端实际端口

3. **前端开发服务器端口可以不同**
   - Vite 开发服务器可以运行在 5678
   - 但 API 请求必须指向后端端口 8000

---

## 系统架构设计原则（避免常见错误）

### 一、配置集中管理原则

#### 问题模式
配置分散在多个文件中，修改时遗漏导致不一致。

#### 设计原则

1. **单一配置源**
   - 端口、URL等配置应该有唯一的定义位置
   - 其他地方通过引用获取，而不是重复定义

2. **配置依赖图**
   ```
   backend/config.py (PORT=8000)
         ↓
   frontend/.env.development (引用后端端口)
         ↓
   frontend/vite.config.ts (代理目标引用环境变量)
   ```

3. **启动时校验**
   - 应用启动时检查配置一致性
   - 不一致时发出警告或拒绝启动

---

### 二、第三方库API兼容性

#### 问题模式
直接使用第三方库API，不检查版本兼容性，升级依赖后代码崩溃。

#### 设计原则

1. **封装第三方库调用**
   ```python
   # ❌ 错误 - 直接使用第三方API
   cookies = browser.cookies(as_dict=True)

   # ✅ 正确 - 封装为项目内部方法
   def get_browser_cookies(browser) -> list:
       """封装DrissionPage的cookies方法，处理版本差异"""
       try:
           return browser.cookies(all_domains=True, all_info=True)
       except TypeError:
           # 降级处理旧版本API
           return browser.cookies()
   ```

2. **版本检测机制**
   - 在应用启动时检测关键依赖版本
   - 记录版本信息到日志
   - 不兼容时发出警告

3. **依赖锁定**
   - 使用 `requirements.lock` 或 `poetry.lock` 锁定版本
   - 升级依赖前必须测试API变化

---

### 三、数据验证的防御性设计

#### 问题模式
验证逻辑过于严格，缺少可选字段就删除整个记录，导致数据丢失。

#### 设计原则

1. **区分必需字段和可选字段**
   ```python
   # ✅ 正确的设计
   @dataclass
   class Session:
       cookies: list        # 必需 - 没有cookies无法工作
       user_info: dict      # 可选 - 有默认值
       created_at: datetime # 必需

       def is_valid(self) -> bool:
           # 只验证必需字段
           return bool(self.cookies)

       def get_display_name(self) -> str:
           # 可选字段提供默认值
           return self.user_info.get("username", "默认用户")
   ```

2. **降级策略**
   - 核心数据缺失 → 记录无效
   - 辅助数据缺失 → 使用默认值，记录有效

3. **永不自动删除数据**
   - 验证失败时标记为无效，而不是删除
   - 让用户或定时任务决定是否清理

---

### 四、进程管理规范

#### 问题模式
多个相同服务进程同时运行，端口冲突或请求被错误进程处理。

#### 设计原则

1. **启动前端口检查**
   - 启动服务前检查端口是否被占用
   - 被占用时提示用户选择：终止旧进程或使用其他端口

2. **PID文件锁定**
   ```python
   # 服务启动时写入PID文件
   PID_FILE = "backend/server.pid"

   def acquire_lock():
       if os.path.exists(PID_FILE):
           old_pid = read_pid(PID_FILE)
           if is_process_running(old_pid):
               raise RuntimeError(f"Server already running (PID: {old_pid})")
       write_pid(PID_FILE, os.getpid())
   ```

3. **优雅关闭**
   - 捕获终止信号，清理资源
   - 删除PID文件
   - 通知依赖服务

---

### 五、日志驱动的可观测性

#### 问题模式
错误发生时没有足够信息定位问题，只能靠猜测。

#### 设计原则

1. **关键路径全覆盖**
   - 每个外部调用（API、数据库、浏览器）前后都要记录
   - 记录输入参数和输出结果

2. **结构化日志**
   ```python
   logger.info("API called", extra={
       "module": "rpa_service",
       "action": "extract_cookies",
       "browser_url": browser.url,
       "cookies_count": len(cookies)
   })
   ```

3. **错误上下文**
   - 捕获异常时记录完整的调用栈
   - 记录导致错误的输入数据
   - 记录错误发生时的系统状态

---

### 六、本次错误的架构反思

| 错误 | 根本原因 | 架构改进 |
|------|----------|----------|
| 端口配置不一致 | 配置分散，无校验 | 集中配置管理 + 启动校验 |
| API参数错误 | 直接调用第三方API | 封装适配层 + 版本检测 |
| Session被删除 | 验证逻辑过严 | 区分必需/可选字段 + 降级策略 |
| 多进程冲突 | 无进程管理 | PID锁 + 启动前检查 |

---

## 2026-03-05 用户信息提取的防错设计

### 错误现象

登录成功后，`extract_user_info` 返回 `None` 或空字典，导致 `user_info` 无效，session 被视为未登录状态。

### 根本原因

1. **选择器过时或不正确**
   - 使用了错误的 CSS 选择器
   - 网站页面结构已更新，旧选择器失效

2. **缺少备选方案**
   - 只依赖一种方式获取数据
   - 没有尝试 JavaScript 执行、localStorage 等其他方式

3. **过早放弃**
   - 一个选择器失败就返回 None
   - 没有尝试所有可能的选择器

4. **没有默认值策略**
   - 返回 None 导致整个 session 无效
   - 应该返回默认值保证基本功能

### ❌ 错误模式：单一选择器 + 返回 None

```python
# ❌ 错误 - 选择器过时，返回 None
def extract_user_info(self, browser) -> Optional[dict]:
    user_info = {}

    # 只尝试一个选择器
    element = browser.find(".user-name")
    if element:
        user_info["username"] = element.text

    # 如果没找到就返回 None
    return user_info if user_info else None
```

### ✅ 正确模式：多选择器 + JavaScript 备选 + 默认值

```python
# ✅ 正确 - 多层防御策略
def extract_user_info(self, browser) -> dict:
    user_info = {}

    # 第一层：尝试多个 CSS 选择器（按优先级）
    username_selectors = [
        ".nav-figure-text",      # BOSS直聘导航栏
        ".info-primary-name",    # 个人中心
        ".user-name",            # 通用
        "[class*='user-name']",  # 模糊匹配
    ]

    for selector in username_selectors:
        try:
            element = browser.find(selector)
            if element:
                text = element.text.strip()
                if 1 < len(text) < 30:  # 合理长度检查
                    user_info["username"] = text
                    break
        except Exception:
            continue

    # 第二层：JavaScript 从 localStorage/window 获取
    if not user_info.get("username"):
        try:
            js_result = browser.run_js("""
                () => {
                    const result = {};
                    // 检查 localStorage
                    for (let i = 0; i < localStorage.length; i++) {
                        const key = localStorage.key(i);
                        if (key && key.includes('user')) {
                            result[key] = localStorage.getItem(key);
                        }
                    }
                    return result;
                }
            """)
            # 从 js_result 中提取用户名...
        except Exception:
            pass

    # 第三层：默认值策略（保证功能可用）
    if not user_info.get("username"):
        user_info = {"username": "BOSS用户", "source": "default"}
        logger.warning("使用默认用户名，页面选择器可能已过时")

    return user_info
```

### 避免此类错误的设计原则

#### 1. 永远不要假设选择器永远有效

```python
# ❌ 错误假设
# "这个选择器昨天还能用，今天一定也能用"

# ✅ 正确态度
# "网站随时可能更新，需要多层备选方案"
```

#### 2. 使用优先级策略

```python
# 优先级从高到低
PRIORITY_LEVELS = [
    "网站特有的选择器",      # 最准确，但可能失效
    "通用的选择器",          # 较稳定
    "JavaScript 执行",       # 可获取隐藏数据
    "localStorage 数据",     # 网站本地存储
    "默认值",                # 最后的保障
]
```

#### 3. 添加详细日志

```python
# ✅ 记录每一步的结果
for selector in selectors:
    try:
        element = browser.find(selector)
        if element:
            logger.info(f"选择器 '{selector}' 成功: {element.text}")
            break
        else:
            logger.debug(f"选择器 '{selector}' 未找到元素")
    except Exception as e:
        logger.debug(f"选择器 '{selector}' 失败: {e}")
```

#### 4. 返回默认值而不是 None

```python
# ❌ 错误 - 返回 None 会导致后续逻辑全部失效
if not user_info:
    return None

# ✅ 正确 - 返回默认值，保证基本功能
if not user_info.get("username"):
    return {"username": "默认用户", "source": "default"}
```

#### 5. 创建探测脚本

当选择器失效时，使用独立的探测脚本来找出正确的选择器：

```bash
# 运行探测脚本
cd backend
python scripts/explore_user_info.py
```

这个脚本会：
1. 打开浏览器让用户登录
2. 登录后自动探测页面结构
3. 找出正确的选择器
4. 生成修复代码建议

### 修改的文件清单

| 文件 | 修改内容 |
|------|----------|
| `backend/app/services/rpa_service.py` | `extract_user_info` 多层防御策略 |
| `backend/rpa/modules/session_manager.py` | `load_session` 更新验证逻辑 |
| `backend/scripts/explore_user_info.py` | 新建探测脚本 |

### 快速检查清单

当用户信息提取失败时：

1. **检查选择器是否过时**
   - [ ] 运行 `python scripts/explore_user_info.py` 探测新选择器
   - [ ] 更新 `extract_user_info` 中的选择器列表

2. **检查 JavaScript 是否执行成功**
   - [ ] 查看日志中是否有 JavaScript 执行错误
   - [ ] 检查 localStorage 中是否有用户数据

3. **检查默认值是否生效**
   - [ ] 日志中应该有 "使用默认用户名" 的警告
   - [ ] 如果没有，说明代码逻辑有问题

4. **检查 session 验证逻辑**
   - [ ] `load_session` 是否正确验证 user_info
   - [ ] 是否因为 user_info 无效而删除了 session

---

## 2026-03-06 浏览器会话自动恢复架构

### 需求背景

用户期望的行为：
1. 每次启动服务，先从数据库中读取 session
2. 如果 session 没有过期 → 直接展示"已登录"界面，**同时自动打开 BOSS 网页**
3. 如果 session 不存在或已过期 → 展示"启动 BOSS 网页"按钮

### 架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                        服务启动流程                               │
├─────────────────────────────────────────────────────────────────┤
│  1. 后端 main.py lifespan 启动                                   │
│     ↓                                                            │
│  2. BrowserRestorer.restore_if_valid_session()                  │
│     ↓                                                            │
│  ┌─────────────────┬─────────────────┐                           │
│  │ session 有效    │ session 无效    │                           │
│  ├─────────────────┼─────────────────┤                           │
│  │ 自动打开浏览器   │ 不打开浏览器     │                           │
│  │ 注入 cookies    │                  │                           │
│  │ 导航到 BOSS     │                  │                           │
│  └─────────────────┴─────────────────┘                           │
│     ↓                    ↓                                        │
│  3. 前端启动，调用 /api/auth/status                               │
│     ↓                    ↓                                        │
│  显示已登录界面      显示"启动BOSS网页"按钮                         │
└─────────────────────────────────────────────────────────────────┘
```

### 核心模块

#### 1. BrowserRestorer（新建）

**文件**: `backend/rpa/modules/browser_restorer.py`

```python
class BrowserRestorer:
    """浏览器会话恢复器 - 服务启动时自动恢复登录状态"""

    async def restore_if_valid_session(self) -> bool:
        """
        检查并恢复浏览器会话
        Returns:
            True: 恢复成功，浏览器已打开
            False: 无有效 session，需要用户手动登录
        """
        # 1. 检查浏览器是否已运行（幂等性）
        if self.browser_manager.is_browser_running():
            return True

        # 2. 加载 session
        session = await self.session_manager.load_session()
        if not session:
            return False

        # 3. 启动浏览器
        browser = self.browser_manager.start_browser()

        # 4. 注入反检测脚本
        AntiDetection.inject_anti_detection_scripts(browser)

        # 5. 注入 cookies
        browser.cookies(session["cookies"])

        # 6. 导航到 BOSS 首页
        browser.get("https://www.zhipin.com")

        # 7. 验证登录状态
        return await self._verify_login_status(browser)
```

#### 2. 状态 API 扩展

**文件**: `backend/app/services/rpa_service.py`

```python
async def get_status(self) -> dict:
    return {
        "is_logged_in": is_logged_in,
        "user_info": user_info,
        "browser_status": browser_health.get("status"),
        "browser_opened": self.browser_manager.is_browser_running(),  # 新增
        "login_in_progress": self._login_in_progress,
    }
```

#### 3. 前端状态同步

**文件**: `frontend/src/App.vue`

```typescript
onMounted(async () => {
  // 1. 先从 localStorage 快速恢复
  authStore.loadFromStorage()

  // 2. 与后端同步验证
  const status = await fetch('/api/auth/status')

  // 情况1: session有效 + 浏览器已打开 → 显示已登录
  if (status.is_logged_in && status.browser_opened) {
    authStore.setAuth({ isAuthenticated: true, user: status.user_info })
  }

  // 情况2: session有效 + 浏览器未打开 → 尝试恢复
  else if (status.is_logged_in && !status.browser_opened) {
    await fetch('/api/auth/restore-browser', { method: 'POST' })
  }

  // 情况3: 无有效session → 清除前端状态
  else {
    authStore.clearAuth()
  }
})
```

### 设计原则

#### 1. 单一职责

- `BrowserRestorer` 只负责恢复浏览器会话
- `RPAService` 负责业务逻辑
- `Auth API` 负责暴露接口

#### 2. 幂等性

```python
# 多次调用不会重复打开浏览器
if self.browser_manager.is_browser_running():
    return True
```

#### 3. 优雅降级

```python
# 恢复失败不阻止服务启动
try:
    restored = await browser_restorer.restore_if_valid_session()
except Exception as e:
    logger.warning(f"Failed to restore: {e}")
    # 继续启动，用户可以手动登录
```

#### 4. 可观测性

每个步骤都有日志记录：
- "Starting browser session restoration..."
- "Valid session found for user: xxx"
- "Browser started successfully"
- "Cookies injected successfully"
- "Browser session restored successfully!"

### 避免的错误

#### 错误1：在 Windows 日志中使用 emoji

```python
# ❌ 错误 - Windows GBK 编码不支持 emoji
logger.info("✅ Browser session restored")

# ✅ 正确 - 使用 ASCII 字符
logger.info("[OK] Browser session restored")
```

#### 错误2：端口配置不一致

```bash
# ❌ 错误 - 后端 .env 和前端配置不一致
# backend/.env
PORT=3000

# frontend/.env.development
VITE_API_BASE_URL=http://localhost:8000

# ✅ 正确 - 统一使用 8000
# backend/.env
PORT=8000

# frontend/.env.development
VITE_API_BASE_URL=http://localhost:8000
```

#### 错误3：前端硬编码 API 地址

```typescript
// ❌ 错误 - 硬编码
const response = await fetch('http://localhost:8000/api/auth/status')

// ✅ 正确 - 使用环境变量
const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const response = await fetch(`${apiBaseUrl}/api/auth/status`)
```

### 修改的文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `backend/rpa/modules/browser_restorer.py` | 新建 | 浏览器会话恢复器 |
| `backend/app/services/rpa_service.py` | 修改 | 添加 `browser_opened` 字段和 `restore_browser_session()` 方法 |
| `backend/app/api/auth.py` | 修改 | 添加 `/restore-browser` API 端点 |
| `backend/app/main.py` | 修改 | 启动时调用 `browser_restorer.restore_if_valid_session()` |
| `backend/.env` | 修改 | 端口从 3000 改为 8000 |
| `frontend/src/App.vue` | 修改 | 优化启动状态同步逻辑，使用环境变量 |
| `frontend/src/views/HomeView.vue` | 修改 | 添加浏览器状态提示和"重新连接"按钮 |

### 测试验证

1. **首次启动（无 session）**
   - 启动服务 → 显示"启动 BOSS 网页"按钮
   - 点击按钮 → 浏览器打开 → 扫码登录 → 显示已登录界面

2. **重启服务（有有效 session）**
   - 关闭服务
   - 重新启动 → 浏览器自动打开 → 直接显示已登录界面

3. **手动恢复**
   - 如果浏览器意外关闭
   - 点击"重新连接"按钮 → 恢复浏览器会话
