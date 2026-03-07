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

---

## 2026-03-06 BOSS 账号管理功能实现总结

### 功能概述

在系统设置页面实现了完整的 BOSS 账号管理功能，支持：
- 多账号管理（HR/求职者类型）
- 账号分组（支持层级结构）
- 标签系统
- 批量操作
- 操作日志
- 配额管理

### 新增文件清单

#### 后端
- `backend/migrations/011_enhance_account_management.sql` - 数据库迁移
- `backend/app/services/account_group_service.py` - 分组管理服务
- `backend/app/api/account_groups.py` - 分组管理 API

#### 前端
- `frontend/src/components/account/AccountManagementTab.vue` - 主管理组件
- `frontend/src/components/account/AccountStatistics.vue` - 统计卡片
- `frontend/src/components/account/AccountToolbar.vue` - 工具栏
- `frontend/src/components/account/AccountList.vue` - 账号列表
- `frontend/src/components/account/AccountCard.vue` - 账号卡片
- `frontend/src/components/account/AccountGroupTree.vue` - 分组树
- `frontend/src/components/account/AccountDetailDrawer.vue` - 详情抽屉
- `frontend/src/components/account/BatchOperationDialog.vue` - 批量操作对话框
- `frontend/src/components/account/AccountGroupDialog.vue` - 分组编辑对话框

### 遇到的问题和解决方案

#### 问题1：数据库字段与代码不匹配

**现象**：创建账号时，数据库中的 `account_type` 字段总是 `seeker`，而不是传入的 `hr`

**原因**：
1. 数据库迁移 003 中 `account_type` 的默认值是 `seeker`
2. `AccountService.create` 方法中使用了 `getattr(account, 'account_type', 'hr')`，但实际上 `account` 对象已经有 `account_type` 属性
3. 代码修改后服务未重启，旧代码仍在运行

**解决方案**：
1. 直接使用 `account.account_type` 而不是 `getattr`
2. 添加调试日志确认数据传递是否正确
3. 确保每次修改代码后重启服务

**预防措施**：
```python
# ❌ 错误 - 使用 getattr 可能返回意外的值
account_type = getattr(account, 'account_type', 'hr')

# ✅ 正确 - 直接访问属性
account_type = account.account_type

# ✅ 也可以 - 添加调试日志确认值
logger.info(f"Account type from request: {account.account_type}")
```

#### 问题2：后端服务端口被占用

**现象**：启动后端服务时报错 "端口已被占用"

**原因**：之前的进程未正确关闭

**解决方案**：
```bash
# 查找并终止占用端口的进程
netstat -ano | findstr ":8000"
taskkill /F /PID <PID>

# 或使用 PowerShell
Stop-Process -Id <PID> -Force
```

**预防措施**：
- 在启动脚本中添加端口检查
- 使用 PID 文件防止重复启动

#### 问题3：前端组件命名冲突

**现象**：`unplugin-vue-components` 报告组件命名冲突

**原因**：
- `components/business/AccountCard.vue`（旧）
- `components/account/AccountCard.vue`（新）

**解决方案**：
- 重命名其中一个组件
- 或者明确导入路径

#### 问题4：Vue 3 Composition API 的 computed 使用错误

**现象**：`mode.value === 'dark'` 报错 `Property 'value' does not exist`

**原因**：`useTheme()` 返回的 `mode` 已经是 `Ref<string>` 类型，但在 `computed` 中应该使用 `.value` 访问

**正确用法**：
```typescript
const { mode } = useTheme()  // mode 是 Ref<ThemeMode>

// ✅ 正确 - 在 computed 中使用 .value
const isDark = computed(() => mode.value === 'dark')

// ❌ 错误 - 直接比较 Ref 对象
const isDark = computed(() => mode === 'dark')  // 总是 false
```

### 最佳实践

#### 1. 数据库迁移设计

```sql
-- ✅ 好的迁移文件应该：
-- 1. 使用 IF NOT EXISTS 避免重复创建
-- 2. 包含回滚说明
-- 3. 添加必要的索引

-- 创建表
CREATE TABLE IF NOT EXISTS account_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    parent_id INTEGER REFERENCES account_groups(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_account_groups_parent ON account_groups(parent_id);
```

#### 2. 服务层方法设计

```python
# ✅ 好的服务方法应该：
# 1. 有明确的类型注解
# 2. 有错误处理
# 3. 有日志记录

async def create(self, account: AccountCreate) -> AccountResponse:
    """创建账户

    Args:
        account: 账户创建模型

    Returns:
        AccountResponse: 创建的账户

    Raises:
        ValueError: 如果手机号已存在
    """
    logger.info(f"Creating account with phone: {account.phone}")

    try:
        # 检查重复
        existing = await self.get_by_phone(account.phone)
        if existing:
            raise ValueError(f"手机号 {account.phone} 已存在")

        # 创建账户
        # ...

    except Exception as e:
        logger.error(f"Error creating account: {e}")
        raise
```

#### 3. 前端组件结构

```typescript
// ✅ 好的组件结构：
// 1. 清晰的 props 和 emits 定义
// 2. 使用 computed 缓存计算结果
// 3. 使用 TypeScript 类型

interface Props {
  account: HRAccount
  selected: boolean
  isActive: boolean
}

interface Emits {
  (e: 'select', accountId: number): void
  (e: 'login', accountId: number): void
  (e: 'refresh', accountId: number): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 使用 computed 缓存
const statusColor = computed(() => {
  return props.account.cookie_status === 'valid' ? 'connected' : 'disconnected'
})
```

### 开发流程建议

1. **修改代码后必须重启服务**
   - 后端：`uvicorn` 有热重载，但有时需要手动重启
   - 前端：Vite 会自动热重载

2. **测试 API 时使用 Python 而不是 curl**
   - Windows 上的 curl 对 JSON 处理有问题
   - Python 的 `requests` 库更可靠

3. **检查数据库状态**
   - 修改后直接查询数据库验证
   - 不要只依赖 API 响应

4. **查看服务日志**
   - 后端日志在控制台输出
   - 前端日志在浏览器开发者工具


## 2026-03-06 数据库列映射防错指南

### 错误模式：硬编码索引

**问题**：迁移添加新列后，原有索引位置会错位

\`\`\`python
# 错误 - 硬编码索引，def _row_to_response(self, row):
    return Response(
        id=row[0],
        phone=row[1],
        group_id=row[5],  # 迁移后可能不是 group_id！
    )
\`\`\`

**原因**：
1. 初始表有 N 列
2. 迁移在末尾添加新列
3. 代码假设的索引与实际列位置不匹配

**正确模式**：

\`\`\`python
# 方案1: 使用 PRAGMA table_info 获取列名
async def _row_to_response(self, row):
    cursor = await self.conn.execute("PRAGMA table_info(table_name)")
    columns = [col[1] for col in await cursor.fetchall()]
    row_dict = dict(zip(columns, row))
    return Response(id=row_dict["id"], phone=row_dict["phone"], ...)

# 方案2: 显式指定列名查询
cursor = await conn.execute(
    "SELECT id, phone, group_id FROM table_name WHERE id = ?", (id,)
)

# 方案3: 使用 aiosqlite.Row 工厂
conn.row_factory = aiosqlite.Row
row = await cursor.fetchone()
return Response(id=row["id"], phone=row["phone"], group_id=row["group_id"])
\`\`\`

---

## 2026-03-06 Schema 与数据库同步防错

### 错误模式：迁移添加列但未更新 Schema

**问题**：数据库有新列但 Response 模型没有对应字段

\`\`\`python
# 迁移添加了 account_type 列
# 但 Schema 没有更新
class AccountResponse(BaseModel):
    id: int
    phone: str
    # 缺少 account_type！
\`\`\`

**防错措施**：

1. **迁移文件必须包含 Schema 更新说明**
   \`\`\`sql
   -- Migration 003
   -- TODO: Add account_type to AccountResponse
   
   ALTER TABLE accounts ADD COLUMN account_type TEXT;
   \`\`\`

2. **添加单元测试验证字段完整性**
   \`\`\`python
   async def test_response_has_all_db_columns():
       cursor = await db.execute("PRAGMA table_info(accounts)")
       db_columns = {col[1] for col in await cursor.fetchall()}
       
       response_fields = set(AccountResponse.model_fields.keys())
       
       # 排除不需要映射的字段
       unmapped = db_columns - response_fields - {"password", "salt"}
       assert not unmapped, f"未映射的数据库列: {unmapped}"
   \`\`\`

---

## 2026-03-06 批量操作事务保护

### 错误模式：无事务保护的批量操作

**问题**：中途失败导致部分数据已修改，无法恢复

\`\`\`python
# 错误 - 无事务保护
for item in items:
    await delete(item.id)  # 第3个失败，前2个已删除
await conn.commit()
\`\`\`

**正确模式**：

\`\`\`python
# 正确 - 使用事务包装器
await conn.execute("BEGIN IMMEDIATE TRANSACTION")
try:
    for item in items:
        await delete(item.id)
    await conn.commit()
except Exception:
    await conn.execute("ROLLBACK")
    raise
\`\`\`

**注意**：SQLite 默认每个语句是自动提交的，必须显式开启事务。

---

## 2026-03-06 前端组件事件防错

### 错误模式：发送 CustomEvent 无监听器

**问题**：组件发送事件但没有监听器，导致功能失效

\`\`\`typescript
// 错误 - 发送 CustomEvent 但没有组件监听
function openDialog() {
  window.dispatchEvent(new CustomEvent('open-dialog'))
}
\`\`\`

**正确模式**：

\`\`\`typescript
// 方案1: 使用组件引用
const dialogRef = ref<InstanceType<typeof Dialog>>()
function openDialog() {
  dialogRef.value?.open()
}

// 方案2: 使用 v-model 控制
const dialogVisible = ref(false)
function openDialog() {
  dialogVisible.value = true
}
\`\`\`

---

## 2026-03-06 重复定义检测

### 错误模式：同一文件中重复定义类

**问题**：复制粘贴或合并冲突导致同一类定义两次

\`\`\`python
# 第 50 行
class LoginRequest(BaseModel):
    phone: str

# 第 150 行（重复！）
class LoginRequest(BaseModel):
    phone: str
\`\`\`

**防错措施**：

1. **代码审查清单**
   - [ ] 搜索文件中所有 `class ` 定义
   - [ ] 检查是否有同名类
   - [ ] 使用 IDE 的 "Go to Definition" 验证

2. **使用 linter**
   \`\`\`bash
   pip install pylint
   pylint --disable=all --enable=duplicate-code app/
   \`\`\`

---

## 2026-03-06 高级功能实现 - Toast/合并/批量/监控

### 需求背景

完成账号自动同步后，需要实现4个高级功能：
1. **Toast通知系统**：替换alert为友好的toast通知
2. **账号合并功能**：检测和合并重复账号
3. **批量操作增强**：批量验证Cookie、批量登录等
4. **账号状态监控**：定时检查Cookie有效性

---

### 关键错误1：FastAPI路由顺序冲突

#### 错误现象

新增 `/api/accounts/duplicates` 端点后，访问时返回错误：
\`\`\`
{"detail": [{"type": "int_parsing", "loc": ["path", "account_id"], "msg": "Input should be a valid integer"}]}
\`\`\`

#### 根本原因

**FastAPI路由匹配按定义顺序，参数化路由 `/{account_id}` 会先匹配 `/duplicates`**

\`\`\`python
# ❌ 错误顺序
@router.get("/{account_id}")  # 第100行
async def get_account(account_id: int):
    ...

@router.get("/duplicates")  # 第200行 - 永远不会被匹配到！
async def detect_duplicates():
    ...
\`\`\`

#### 正确模式

**具体路由必须在参数化路由之前定义**

\`\`\`python
# ✅ 正确顺序
@router.get("/duplicates")  # 具体路径在前
async def detect_duplicates():
    ...

@router.get("/{account_id}")  # 参数化路径在后
async def get_account(account_id: int):
    ...
\`\`\`

#### 防错措施

1. **路由定义顺序检查清单**
   - [ ] 所有具体路径 (`/duplicates`, `/statistics`, `/batch`) 在前
   - [ ] 所有参数化路径 (`/{id}`, `/{account_id}`) 在后
   - [ ] 嵌套参数路径 (`/{id}/logs`, `/{id}/validate`) 在最后

2. **使用FastAPI路由排序工具**
   \`\`\`python
   # 在开发环境中列出所有路由
   from fastapi.routing import APIRoute
   for route in app.routes:
       if isinstance(route, APIRoute):
           print(f"{route.methods} {route.path}")
   \`\`\`

3. **API文档生成时检查**
   - FastAPI自动生成的文档（`/docs`）会显示路由顺序
   - 检查是否有路由被"隐藏"（应该显示但没显示）

---

### 关键错误2：重复路由定义

#### 错误现象

同一文件中定义了两次相同的路由：
\`\`\`python
# 第40行
@router.get("/duplicates")
async def detect_duplicate_accounts():
    ...

# 第332行（重复！）
@router.get("/duplicates")
async def detect_duplicate_accounts():
    ...
\`\`\`

#### 根本原因

1. 复制粘贴后忘记删除旧代码
2. 代码合并时没有清理重复部分
3. IDE自动完成创建了重复定义

#### 防错措施

1. **搜索重复定义**
   \`\`\`bash
   # 搜索重复的路由定义
   grep -n "^@router\.(get|post|put|delete)" app/api/accounts.py | grep "duplicates"
   \`\`\`

2. **使用Python的命名空间检查**
   - 同一文件中不能有两个同名函数
   - IDE会显示警告

3. **代码审查清单**
   - [ ] 检查是否有重复的 `@router` 装饰器
   - [ ] 检查是否有重复的函数名
   - [ ] 使用 `grep` 验证没有重复

---

### 关键错误3：服务重载失败

#### 错误现象

修改代码后，uvicorn热重载没有生效，API还是返回旧代码的结果。

#### 根本原因

1. **文件保存但uvicorn没有检测到变化**
2. **Python缓存（.pyc文件）导致旧代码被执行**
3. **多个进程监听同一端口**

#### 防错措施

1. **验证服务重载成功**
   \`\`\`bash
   # 检查日志中是否有 "Reloading..." 消息
   tail -f backend/logs/app.log | grep "Reloading"
   \`\`\`

2. **清理Python缓存**
   \`\`\`bash
   # 删除所有.pyc缓存文件
   find backend -name "*.pyc" -delete
   find backend -name "__pycache__" -type d -exec rm -rf {} +
   \`\`\`

3. **强制重启服务**
   \`\`\`bash
   # 终止所有相关进程
   netstat -ano | grep ":8000"
   taskkill /F /PID <pid>

   # 重新启动
   cd backend && uv run uvicorn app.main:app --reload
   \`\`\`

4. **验证API端点可用**
   \`\`\`bash
   # 检查OpenAPI文档
   curl http://localhost:8000/docs | grep "duplicates"

   # 或直接测试端点
   curl http://localhost:8000/api/accounts/duplicates
   \`\`\`

---

### 实施要点总结

#### 1. 全局错误处理器设计

\`\`\`typescript
// frontend/src/utils/errorHandler.ts
export function setupErrorHandling() {
  // 1. 全局同步错误
  window.onerror = (message, source, lineno, colno, error) => {
    toast.error(\`系统错误: \${message}\`)
    return false
  }

  // 2. Promise未捕获错误
  window.addEventListener('unhandledrejection', (event) => {
    toast.error(\`异步错误: \${event.reason}\`)
  })
}
\`\`\`

#### 2. 账号合并服务设计

\`\`\`python
# backend/app/services/account_merge_service.py
class AccountMergeService:
    async def detect_duplicates(self) -> List[DuplicateGroup]:
        """检测重复账号：按手机号和用户名分组"""

    async def preview_merge(self, source_id: int, target_id: int) -> MergePreview:
        """预览合并：显示将要迁移的数据"""

    async def merge_accounts(self, source_id: int, target_id: int, strategy: str) -> MergeResult:
        """执行合并：事务保护，迁移sessions和logs"""
\`\`\`

#### 3. Toast替换模式

\`\`\`typescript
// ❌ 错误
alert('操作失败')

// ✅ 正确
import { useToast } from '@/composables/useToast'
const toast = useToast()
toast.error('操作失败')
\`\`\`

---

### 关键文件清单

#### 后端新增
- `backend/app/services/account_merge_service.py` - 账号合并服务
- `backend/app/utils/toast.py` - Toast工具（可选）

#### 后端修改
- `backend/app/api/accounts.py` - 添加合并API（注意路由顺序！）

#### 前端新增
- `frontend/src/utils/errorHandler.ts` - 全局错误处理器

#### 前端修改
- `frontend/src/main.ts` - 集成错误处理
- `frontend/src/components/account/AccountManagementTab.vue` - 替换alert

---

### 测试验证清单

- [ ] 后端服务启动无错误
- [ ] `/api/accounts/duplicates` 端点可访问
- [ ] 前端错误自动显示toast
- [ ] 账号合并功能正常工作
- [ ] 没有重复的路由定义

---

## 2026-03-06 BOSS账号自动同步功能实现

### 需求背景

**核心问题**：登录流程与账号管理系统割裂
- 用户通过通用登录（`/api/auth/login`）登录新账号后，session只保存到`sessions`表（单例模式）
- 账号管理系统（`accounts`表）不会自动更新
- 导致登录的新账号无法出现在账号管理界面，无法切换使用

**业务目标**：
- 登录后自动同步到账号系统，无需手动创建
- 所有登录过的账号集中管理，随时切换
- 统一维护所有账号的会话和状态

---

### 架构设计原则

#### 1. 模块化设计

```
登录流程（不破坏现有功能）
    ↓
RPAService._handle_login_success()
    ↓
[新增] AccountSyncService.sync_account_from_login()
    ├─ identify_account() → 识别账号
    ├─ create_or_update_account() → 更新accounts表
    ├─ save_session_for_account() → 保存到account_sessions
    └─ [保留] save_session() → 向后兼容sessions表
    ↓
前端收到 account_id，显示提示
```

#### 2. 核心设计原则
- **单一职责**：AccountSyncService 只负责账号同步
- **开闭原则**：不修改现有核心逻辑，只增加新模块
- **依赖倒置**：RPAService 依赖抽象的同步接口
- **防御性编程**：多层识别策略 + 降级方案
- **幂等性**：多次登录同一账号不创建重复记录

---

### 实施步骤

#### Phase 1: 数据库迁移（15分钟）

**迁移文件**: `backend/migrations/012_add_account_sync_fields.sql`

```sql
-- 添加同步相关字段
ALTER TABLE accounts ADD COLUMN auto_created BOOLEAN DEFAULT 0;
ALTER TABLE accounts ADD COLUMN last_sync_at TIMESTAMP;
ALTER TABLE accounts ADD COLUMN sync_source TEXT DEFAULT 'manual';
-- sync_source 可选值: 'manual', 'auto_login', 'import', 'auto_migration'

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_accounts_auto_created ON accounts(auto_created);
CREATE INDEX IF NOT EXISTS idx_accounts_sync_source ON accounts(sync_source);
```

**验证方法**：
```bash
# 迁移会在应用启动时自动执行
# 验证字段
sqlite3 data/boss_rpa.db "PRAGMA table_info(accounts)"
```

---

#### Phase 2: 后端核心服务（45分钟）

##### 2.1 创建账号同步服务

**文件**: `backend/app/services/account_sync_service.py`（新建）

**核心功能**：
1. `identify_account(user_info)` - 识别账号
   - 策略1：通过手机号匹配（优先级最高）
   - 策略2：通过用户名匹配（次优先级）
   - 策略3：返回None（新账号）

2. `sync_account_from_login(cookies, user_info)` - 同步账号
   - 调用 identify_account 判断是否已有账号
   - 创建或更新 accounts 表
   - 保存到 account_sessions 表
   - 返回 SyncResult(account_id, is_new_account, message)

**关键代码模式**：

```python
async def identify_account(self, user_info: dict) -> Optional[int]:
    """识别账号 - 多策略组合"""
    # 策略1：手机号匹配
    phone = user_info.get("phone")
    if phone:
        cursor = await self.conn.execute(
            "SELECT id FROM accounts WHERE phone = ?", (phone,)
        )
        row = await cursor.fetchone()
        if row:
            return row[0]

    # 策略2：用户名匹配
    username = user_info.get("username")
    if username and username != "BOSS用户":  # 排除默认值
        cursor = await self.conn.execute(
            "SELECT id FROM accounts WHERE username = ?", (username,)
        )
        row = await cursor.fetchone()
        if row:
            return row[0]

    return None  # 新账号
```

##### 2.2 修改 RPAService

**文件**: `backend/app/services/rpa_service.py`

**修改位置**: `_handle_login_success()` 方法

**关键点**：
- 使用 try-except 包裹同步逻辑，失败不影响登录
- 保留原有的 save_session 调用（向后兼容）
- 返回值增强，包含 account_id, is_new_account, sync_message

```python
async def _handle_login_success(self, browser) -> dict[str, Any]:
    # Extract cookies and user_info
    cookies = self.extract_cookies(browser)
    user_info = self.extract_user_info(browser)

    # ========== 新增：自动同步到账号系统 ==========
    try:
        sync_service = AccountSyncService(conn)
        sync_result = await sync_service.sync_account_from_login(
            cookies=cookies, user_info=user_info
        )
    except Exception as sync_error:
        logger.error(f"Account sync failed: {sync_error}")
        # 同步失败不影响登录
        sync_result = {...}
    # =============================================

    # 保留原有的保存到 sessions 表（向后兼容）
    await self.session_manager.save_session(cookies, user_info)

    return {
        "status": "success",
        "user_info": user_info,
        "account_id": sync_result.account_id,  # 新增
        "is_new_account": sync_result.is_new_account,
        "sync_message": sync_result.message
    }
```

##### 2.3 增强 API 返回值

**文件**: `backend/app/api/auth.py`

**修改位置**: `monitor_and_broadcast_login()` 函数

```python
if result["status"] == "success":
    status = await rpa_service.get_status()

    # 增强返回数据
    status["account_id"] = result.get("account_id")
    status["is_new_account"] = result.get("is_new_account")
    status["sync_message"] = result.get("sync_message")

    await broadcast_status(status)
```

---

#### Phase 3: 前端适配（30分钟）

##### 3.1 处理登录成功消息

**文件**: `frontend/src/composables/useWebSocket.ts`

**关键修改**：
```typescript
case 'status_update':
  const accountId = data.data?.account_id  // 新增
  const isNewAccount = data.data?.is_new_account  // 新增
  const syncMessage = data.data?.sync_message  // 新增

  if (isLoggedIn && hasValidUserInfo) {
    authStore.setAuth({
      isAuthenticated: true,
      user: userInfo,
      accountId: accountId  // 新增
    })

    // 显示同步提示
    if (syncMessage) {
      console.log(`${isNewAccount ? '✓' : '↻'} ${syncMessage}`)
    }

    // 刷新账号列表
    if (accountId) {
      hrStore.loadAccounts()
    }
  }
```

##### 3.2 更新 authStore

**文件**: `frontend/src/stores/auth.ts`

**新增字段**：
```typescript
const accountId = ref<number | null>(null)  // 新增

function setAuth(authData: { ..., accountId?: number | null }) {
  accountId.value = isValidAuth ? (authData.accountId || null) : null

  // 持久化
  localStorage.setItem('auth', JSON.stringify({
    isAuthenticated: true,
    user: authData.user,
    accountId: authData.accountId  // 新增
  }))
}
```

---

### 避免的错误模式

#### 错误1：同步失败导致登录失败

**错误模式**：
```python
# ❌ 错误 - 同步失败会阻止登录
sync_result = await sync_service.sync_account_from_login(cookies, user_info)
if not sync_result.account_id:
    raise Exception("Sync failed")
```

**正确模式**：
```python
# ✅ 正确 - 同步失败不影响登录
try:
    sync_result = await sync_service.sync_account_from_login(cookies, user_info)
except Exception as sync_error:
    logger.error(f"Account sync failed: {sync_error}")
    sync_result = {"account_id": None, "is_new_account": False, "message": "同步失败"}
```

---

#### 错误2：缺少向后兼容

**错误模式**：
```python
# ❌ 错误 - 移除了原有逻辑
# await self.session_manager.save_session(cookies, user_info)  # 删除了！
```

**正确模式**：
```python
# ✅ 正确 - 保留原有逻辑
await self.session_manager.save_session(cookies, user_info)  # 向后兼容
```

---

#### 错误3：账号重复创建

**错误模式**：
```python
# ❌ 错误 - 不检查是否已有账号
account_id = await create_account(user_info)
```

**正确模式**：
```python
# ✅ 正确 - 先识别再创建
account_id = await self.identify_account(user_info)
if not account_id:
    account_id = await self._create_auto_account(user_info, cookies)
```

---

#### 错误4：前端未刷新账号列表

**错误模式**：
```typescript
// ❌ 错误 - 登录成功后不刷新列表
authStore.setAuth({ isAuthenticated: true, user: userInfo })
```

**正确模式**：
```typescript
// ✅ 正确 - 登录成功后刷新账号列表
authStore.setAuth({ isAuthenticated: true, user: userInfo, accountId })
if (accountId) {
  hrStore.loadAccounts()  // 刷新账号列表
}
```

---

### 边界情况处理

#### 1. user_info 不完整

**场景**：提取不到用户名或手机号

**处理**：
- 使用默认用户名 "BOSS用户"
- 标记为 `auto_created=1`
- 记录警告日志
- 不影响登录流程

```python
if not user_info or not user_info.get("username"):
    user_info = {"username": "BOSS用户", "source": "default", "auto_created": True}
    logger.warning("Using default user info due to missing data")
```

---

#### 2. 手机号冲突

**场景**：user_info 中没有手机号，但需要创建账号

**处理**：
- 生成临时手机号避免冲突
- 格式：`auto_{timestamp}`

```python
phone = user_info.get("phone")
if not phone:
    import time
    timestamp = int(time.time() * 1000)
    phone = f"auto_{timestamp}"
```

---

#### 3. 用户名是默认值

**场景**：提取到的用户名是 "BOSS用户"（默认值）

**处理**：
- 识别账号时排除默认值
- 避免将所有默认用户名的账号识别为同一账号

```python
username = user_info.get("username")
if username and username != "BOSS用户":  # 排除默认值
    # 尝试匹配
```

---

### 数据库字段说明

#### accounts 表新增字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `auto_created` | BOOLEAN | 0 | 是否为自动创建的账号 |
| `last_sync_at` | TIMESTAMP | NULL | 最后同步时间 |
| `sync_source` | TEXT | 'manual' | 同步来源 |

**sync_source 可选值**：
- `manual` - 手动创建
- `auto_login` - 登录自动同步
- `import` - 批量导入
- `auto_migration` - 迁移脚本创建

---

### 测试验证清单

#### 后端测试
- [ ] 迁移文件执行成功
- [ ] accounts 表新增字段存在
- [ ] 登录成功后 accounts 表有新记录
- [ ] account_sessions 表有对应记录
- [ ] sessions 表仍然正常工作（向后兼容）
- [ ] 重复登录同一账号不会创建重复记录

#### 前端测试
- [ ] 登录成功后显示同步提示
- [ ] 账号管理界面出现新账号
- [ ] 账号列表自动刷新
- [ ] localStorage 包含 accountId
- [ ] 刷新页面后状态恢复

#### 集成测试
- [ ] 首次登录新账号 → 自动创建
- [ ] 已有账号重新登录 → 更新状态
- [ ] 账号切换功能正常
- [ ] Cookie 状态正确显示

---

### 关键文件清单

#### 后端新增文件
- `backend/migrations/012_add_account_sync_fields.sql` - 数据库迁移
- `backend/app/services/account_sync_service.py` - 账号同步服务

#### 后端修改文件
- `backend/app/services/rpa_service.py` - 修改 `_handle_login_success()` 方法
- `backend/app/api/auth.py` - 增强 WebSocket 返回值

#### 前端修改文件
- `frontend/src/composables/useWebSocket.ts` - 处理同步消息
- `frontend/src/stores/auth.ts` - 添加 accountId 字段

---

### 预期成果

#### 功能成果
1. ✅ 登录新账号后自动同步到账号管理系统
2. ✅ 账号管理界面实时显示所有登录过的账号
3. ✅ 前端显示友好的同步提示
4. ✅ 支持账号无缝切换

#### 架构成果
1. ✅ 模块化设计，易于维护和扩展
2. ✅ 防御性编程，处理各种边界情况
3. ✅ 向后兼容，不破坏现有功能
4. ✅ 完整的测试覆盖

#### 数据完整性
1. ✅ 统一维护 `sessions`、`accounts`、`account_sessions` 三张表
2. ✅ 自动标记同步来源和时间
3. ✅ 支持后续的账号合并和清理

---

## 2026-03-06 Vue 组件开发常见错误预防

### 错误1: 使用未定义的变量

**错误现象**:
```
ReferenceError: currentAccountId is not defined
```

**错误模式**:
```typescript
// ❌ 错误 - currentAccountId 从未定义
toast.success(currentAccountId.value ? '账号已更新' : '账号已创建')
```

**正确模式**:
```typescript
// ✅ 正确 - 使用已定义的 editingAccount
const editingAccount = ref<any>(null)
toast.success(editingAccount.value ? '账号已更新' : '账号已创建')
```

**预防措施**:
1. **使用 TypeScript 严格模式** - 会检测未定义变量
   ```typescript
   // tsconfig.json
   {
     "compilerOptions": {
       "strict": true,
       "noImplicitAny": true
     }
   }
   ```

2. **在定义 ref 时立即初始化**
   ```typescript
   // ✅ 立即初始化
   const editingAccount = ref<any>(null)
   const accountFormVisible = ref(false)
   ```

3. **使用变量前先搜索确认**
   - IDE 快捷键: Ctrl+F / Cmd+F
   - 确认变量已在文件顶部定义

4. **IDE 配置**
   - 启用 "拼写检查"
   - 启用 "未定义变量" 警告
   - 使用 ESLint 规则: `no-undef`

---

### 错误2: 组件导入但未在模板中使用

**错误现象**:
```
点击"添加账号"按钮无反应
Vue DevTools 中看不到组件实例
```

**错误模式**:
```vue
<script setup>
// ❌ 错误 - 只导入了组件，状态和方法都准备好了
import AccountFormDialog from './AccountFormDialog.vue'

const accountFormVisible = ref(false)
const editingAccount = ref<any>(null)
const accountFormLoading = ref(false)

function openAddDialog() {
  editingAccount.value = null
  accountFormVisible.value = true  // 设置为 true，但组件不会显示
}

function handleSaveAccount(data: any) {
  // 保存逻辑...
}
</script>

<template>
  <div>
    <button @click="openAddDialog">添加账号</button>
    <!-- ❌ 错误 - 模板中完全没有使用组件 -->
  </div>
</template>
```

**正确模式**:
```vue
<script setup>
// ✅ 正确 - 三要素齐全
import AccountFormDialog from './AccountFormDialog.vue'

const accountFormVisible = ref(false)
const editingAccount = ref<any>(null)
const accountFormLoading = ref(false)

function openAddDialog() {
  editingAccount.value = null
  accountFormVisible.value = true
}

function handleSaveAccount(data: any) {
  // 保存逻辑...
}
</script>

<template>
  <div>
    <button @click="openAddDialog">添加账号</button>

    <!-- ✅ 正确 - 在模板中使用组件 -->
    <AccountFormDialog
      v-model:visible="accountFormVisible"
      :account="editingAccount"
      :loading="accountFormLoading"
      @save="handleSaveAccount"
    />
  </div>
</template>
```

**预防措施**:
1. **组件三要素检查清单**:
   - [ ] 导入组件 (`import Xxx from ...`)
   - [ ] 定义状态 (`const xxxVisible = ref(false)`)
   - [ ] 模板中使用 (`<Xxx v-model:visible="xxxVisible" />`)

2. **添加组件时的正确顺序**:
   ```bash
   # 第1步: 导入组件
   import AccountFormDialog from './AccountFormDialog.vue'

   # 第2步: 立即在模板中添加组件
   <AccountFormDialog v-model:visible="accountFormVisible" />

   # 第3步: 定义状态变量
   const accountFormVisible = ref(false)

   # 第4步: 实现事件处理函数
   function handleSave() { ... }

   # 第5步: 绑定 props 和 events
   <AccountFormDialog
     v-model:visible="accountFormVisible"
     @save="handleSave"
   />
   ```

3. **使用 Vue DevTools 检查**
   - 打开 Vue DevTools
   - 查看组件树
   - 确认组件是否实际渲染

4. **编写组件时立即使用**
   - ❌ 不要: 先导入，后使用
   - ✅ 应该: 导入后立即在模板中声明

---

### 错误3: 后端API已实现但前端无入口

**错误现象**:
```
后端 API 文档中有 /api/accounts/duplicates
但前端界面找不到"检测重复"按钮
```

**错误模式**:
```python
# ❌ 后端已有 API
@router.get("/duplicates")
async def detect_duplicates(): ...
```

```vue
<!-- ❌ 前端完全没有入口 -->
<template>
  <button>添加账号</button>
  <!-- 没有"检测重复"按钮 -->
</template>

<script setup>
// ❌ 没有调用 API 的函数
</script>
```

**正确模式**:
```vue
<template>
  <button @click="handleDetectDuplicates">检测重复</button>
</template>

<script setup>
async function handleDetectDuplicates() {
  const response = await fetch('/api/accounts/duplicates')
  const result = await response.json()
  // 处理结果...
}
</script>
```

**预防措施**:
1. **API-UI 同步检查**: 添加新 API 时，同步添加前端入口
   ```bash
   # 新增 API 后的检查清单
   - [ ] 后端 API 实现
   - [ ] 前端按钮/链接
   - [ ] 前端调用函数
   - [ ] 状态管理
   - [ ] 错误处理
   ```

2. **使用 API 文档验证**:
   - Swagger UI (`/docs`) 列出所有 API
   - 逐一检查前端是否有对应入口
   - 标记已实现和未实现的 API

3. **定期代码审查**:
   ```bash
   # 每周检查
   - 未使用的前端组件
   - 未调用的后端 API
   - 功能完整度对比
   ```

4. **前后端同步开发**:
   - API 设计文档 → 后端实现 → 前端入口
   - 使用 OpenAPI 规范
   - 自动生成前端 API 客户端

---

### 检查清单：Vue 组件开发

#### 开发新组件时

- [ ] **组件文件**: 创建 `.vue` 文件
- [ ] **Props 定义**: 使用 TypeScript 接口
- [ ] **Emits 定义**: 明确事件类型
- [ ] **状态管理**: 使用 `ref` / `reactive`
- [ ] **模板实现**: 组件 HTML 结构
- [ ] **样式实现**: CSS / Tailwind
- [ ] **导入组件**: 在父组件中导入
- [ ] **使用组件**: 在父组件模板中声明
- [ ] **绑定事件**: 处理组件交互

#### 修改现有组件时

- [ ] **搜索变量**: 确认变量已定义
- [ ] **检查类型**: TypeScript 类型正确
- [ ] **测试功能**: 手动测试所有修改点
- [ ] **检查其他文件**: 是否有类似问题需要修复

---

### 快速修复指南

#### 运行时错误: `ReferenceError: xxx is not defined`

1. 定位错误行号
2. 搜索变量名在文件中是否定义
3. 如果未定义，添加定义或使用正确的变量名
4. 如果已定义，检查拼写是否一致

#### 组件不显示问题

1. 检查组件是否导入
2. 检查 `v-if` / `v-show` 条件
3. 检查 `visible` prop 是否为 `true`
4. 使用 Vue DevTools 查看组件树

#### API 调用无响应

1. 检查后端服务是否运行
2. 检查 API 路径是否正确
3. 检查前端是否有入口按钮
4. 检查网络请求是否发送
3. ✅ 支持后续的账号合并和清理

---

## 2026-03-06 账号登录功能重构与浏览器会话恢复

### 需求背景

将 BOSS 网页登录功能从主页移到账号管理页面，每个账号卡片都有独立的登录按钮，并支持浏览器会话恢复。

### 实现的功能

1. **账号管理页面登录**：每个账号卡片上有登录按钮
2. **浏览器会话恢复**：当 cookie 有效但浏览器未运行时，可恢复会话
3. **账号状态同步**：登录成功后自动刷新账号列表

### 新增的 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/auth/accounts/{account_id}/restore-browser` | POST | 为指定账号恢复浏览器会话 |

### 修改的文件

| 文件 | 修改内容 |
|------|----------|
| `backend/app/api/auth.py` | 添加账号浏览器恢复 API |
| `backend/app/services/rpa_service.py` | 添加 `restore_browser_session_for_account()` 方法 |
| `frontend/src/components/account/AccountCard.vue` | 添加"恢复会话"按钮和相关 props |
| `frontend/src/components/account/AccountList.vue` | 透传新的 props 和 events |
| `frontend/src/components/account/AccountManagementTab.vue` | 添加浏览器状态追踪和恢复处理 |

---

### 关键错误1：DrissionPage Cookie API 使用错误

#### 错误现象

```
'ChromiumPageSetter' object has no attribute 'cookie'
```

#### 根本原因

DrissionPage 4.x 中设置 cookie 的 API 不是 `browser.set.cookie()`，而是 `browser.cookies(cookies_list)` 批量设置。

#### ❌ 错误模式

```python
# 错误 - 逐个设置 cookie
for cookie_dict in cookies:
    browser.set.cookie(
        name=cookie_dict.get("name"),
        value=cookie_dict.get("value"),
        domain=cookie_dict.get("domain"),
    )
```

#### ✅ 正确模式

```python
# 正确 - 批量设置 cookies
browser.cookies(cookies)  # cookies 是一个列表
```

#### 防错措施

1. **查看现有实现**：在编写新代码前，先搜索项目中已有的类似实现
2. **参考 browser_restorer.py**：这个文件已经正确实现了 cookie 注入
3. **单元测试**：添加 cookie 相关的单元测试

---

### 关键错误2：多进程占用同一端口

#### 错误现象

- 修改代码后 API 仍然返回旧结果
- OpenAPI 文档中没有新添加的路由
- uvicorn 热重载不生效

#### 根本原因

多个 uvicorn 进程同时监听同一端口（8000），旧进程响应请求。

#### 排查方法

```bash
# 检查端口占用
netstat -ano | findstr ":8000"

# 如果有多个 LISTENING 进程，说明有问题
```

#### 解决方案

```bash
# Windows: 杀掉所有占用端口的进程
for /f "tokens=5" %a in ('netstat -ano ^| findstr ":8000"') do taskkill /F /PID %a

# 然后重新启动服务
cd backend && uv run uvicorn app.main:app --reload --port 8000
```

#### 防错措施

1. **启动前检查端口**：启动服务前先检查端口是否被占用
2. **使用 PID 文件**：记录服务进程 ID，避免重复启动
3. **优雅关闭**：使用 Ctrl+C 关闭服务，而不是直接关闭终端

---

### 关键错误3：前端组件 Props 透传遗漏

#### 错误现象

新添加的按钮不显示或点击无反应。

#### 根本原因

在多层组件结构中，中间组件没有透传新的 props 和 events。

#### 组件层级

```
AccountManagementTab.vue
  └─ AccountList.vue (需要透传)
      └─ AccountCard.vue (实际使用)
```

#### 检查清单

- [ ] AccountCard.vue: 定义了新的 props 和 emits
- [ ] AccountList.vue: 接收 props 并透传给 AccountCard
- [ ] AccountList.vue: 定义了新的 emit 并透传事件
- [ ] AccountManagementTab.vue: 传递 props 并监听事件

#### 透传模式

```vue
<!-- AccountList.vue -->
<template>
  <AccountCard
    :browser-running="browserStatus?.[account.id]"
    :is-restoring-browser="restoringAccountId === account.id"
    @restore-browser="$emit('restore-browser', $event)"
  />
</template>

<script setup>
defineProps<{
  browserStatus?: Record<number, boolean>
  restoringAccountId?: number | null
}>()

defineEmits<{
  'restore-browser': [accountId: number]
}>()
</script>
```

---

### 架构设计原则

#### 1. 账号登录流程

```
用户点击账号卡片"登录"按钮
    ↓
AccountCard emit('login', accountId)
    ↓
AccountManagementTab.handleLogin(accountId)
    ↓
useAccountLogin.loginAccount(accountId)
    ↓
POST /api/auth/login/account { account_id }
    ↓
RPAService.start_login_for_account(accountId)
    ├─ 启动浏览器
    ├─ 导航到登录页
    └─ 启动后台监控任务
    ↓
登录成功 → save_session_for_account(accountId, cookies, user_info)
    ↓
WebSocket 广播 account_login_success
    ↓
前端更新状态和账号列表
```

#### 2. 浏览器会话恢复流程

```
用户点击"恢复会话"按钮
    ↓
AccountCard emit('restore-browser', accountId)
    ↓
AccountManagementTab.handleRestoreBrowser(accountId)
    ↓
POST /api/auth/accounts/{accountId}/restore-browser
    ↓
RPAService.restore_browser_session_for_account(accountId)
    ├─ 验证账号存在
    ├─ 加载账号 session
    ├─ 关闭现有浏览器（如有）
    ├─ 启动新浏览器
    ├─ 注入反检测脚本
    ├─ 注入 cookies（批量设置）
    ├─ 导航到 BOSS 首页
    ├─ 设置为活跃账号
    └─ 更新最后使用时间
    ↓
返回恢复结果
```

---

### 测试验证清单

#### 账号登录功能

- [ ] 主页未登录状态显示"前往账号管理"按钮
- [ ] 账号管理页面显示所有账号
- [ ] 每个账号卡片有登录按钮
- [ ] 点击登录按钮打开浏览器
- [ ] 扫码登录成功后 session 保存正确
- [ ] cookie_status 更新为 'valid'
- [ ] 账号列表自动刷新

#### 浏览器会话恢复功能

- [ ] cookie 有效但浏览器未运行时显示"恢复会话"按钮
- [ ] 点击恢复按钮后浏览器打开
- [ ] 恢复后自动登录到 BOSS
- [ ] 恢复后账号状态正确

#### 错误处理

- [ ] 账号不存在时显示友好提示
- [ ] session 无效时显示友好提示
- [ ] 网络错误时显示友好提示

