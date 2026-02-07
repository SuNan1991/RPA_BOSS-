# Proposal: Industrial-Grade Logging System with Loguru

## Why

当前的日志系统存在以下问题，无法满足工业级应用的需求：

1. **日志分散且不统一**：各模块使用不同的日志方式（print、logging模块、自定义logger），缺乏统一的日志格式和管理
2. **缺乏日志持久化**：日志只输出到控制台，应用重启后丢失历史日志，无法进行问题追溯和分析
3. **前端无法查看后端日志**：开发者和运维人员需要登录服务器查看日志文件，调试和监控困难
4. **缺乏日志级别控制**：无法根据环境动态调整日志详细程度，开发和生产环境使用相同配置
5. **缺乏结构化日志**：日志是纯文本，难以进行日志分析、搜索和可视化
6. **缺乏关键业务信息**：RPA操作的详细过程、用户行为、系统异常等关键信息没有被完整记录

现在需要建立一个**工业级、模块化、可扩展**的日志系统，以支持生产环境的监控、调试和审计需求。

## What Changes

### 核心变更
- **NEW**: 引入 loguru 作为统一日志框架，替换现有的 logging 模块
- **NEW**: 实现日志双输出机制（文件持久化 + 前端实时展示）
- **NEW**: 创建统一的日志配置和管理模块
- **NEW**: 实现结构化日志输出（JSON 格式支持日志分析）
- **NEW**: 添加日志轮转（rotation）和压缩功能，防止日志文件过大
- **NEW**: 实现日志级别动态调整（通过 API 或配置文件）
- **NEW**: 为 RPA 操作添加详细的业务日志记录
- **BREAKING**: 移除所有 `print()` 语句，统一使用 logger
- **BREAKING**: 改变日志文件存储位置和命名规范

### 功能特性
- **双输出模式**：日志同时写入文件和发送到前端 WebSocket
- **文件管理**：自动轮转（按大小、时间）、压缩、清理过期日志
- **结构化日志**：JSON 格式可选，支持 ELK/Loki 等日志系统
- **模块化 logger**：每个模块有独立的 logger，支持单独配置级别
- **上下文信息**：自动注入请求 ID、用户 ID、会话 ID 等追踪信息
- **性能监控**：记录 RPA 操作耗时、数据库查询性能等
- **异常捕获**：全局异常处理器，记录未捕获的异常和堆栈
- **敏感信息过滤**：自动过滤密码、Token 等敏感字段

## Capabilities

### New Capabilities

- **`centralized-logging`**: 统一的日志管理系统，提供全局日志配置、logger 工厂、日志级别管理
- **`log-persistence`**: 日志持久化能力，负责日志文件的创建、轮转、压缩和清理
- **`real-time-log-streaming`**: 实时日志流传输能力，通过 WebSocket 将后端日志推送到前端展示
- **`structured-logging`**: 结构化日志能力，支持 JSON 格式输出和字段提取
- **`rpa-operation-logging`**: RPA 操作专用日志能力，记录浏览器操作、用户行为、业务流程

### Modified Capabilities

- 无（这是全新功能，不修改现有需求规范）

## Impact

### 代码影响

**后端 Python 代码**：
- 新增 `backend/app/core/logging.py` - 统一日志配置和管理
- 新增 `backend/app/middleware/logging_middleware.py` - HTTP 请求日志中间件
- 新增 `backend/app/api/logs.py` - 日志查询和配置 API
- 新增 `backend/app/websockets/log_streamer.py` - WebSocket 日志流推送
- 修改 `backend/app/main.py` - 集成全局异常处理和日志中间件
- 修改所有 RPA 模块 - 替换 print 为 logger 调用

**前端 Vue 代码**：
- 新增 `frontend/src/components/LogViewer.vue` - 实时日志查看器组件
- 新增 `frontend/src/composables/useLogStream.ts` - WebSocket 日志流 composable
- 新增 `frontend/src/stores/logs.ts` - 日志状态管理
- 修改 `frontend/src/components/AuthenticatedPage.vue` - 添加日志查看入口

**依赖变更**：

**后端新增**：
- `loguru` - 已在 pyproject.toml 中，需要启用
- `python-json-logger` - 可选，用于结构化日志 JSON 序列化

**配置文件变更**：
- 新增 `backend/config/logging_config.yaml` - 日志配置文件

### 架构影响

**日志架构变化**：
```
旧架构：各模块独立使用 logging 或 print
新架构：
   Application Layer
   └── Centralized Logging Manager
       ├── File Handler (rotation + compression)
       ├── WebSocket Handler (real-time streaming)
       ├── Filter (sensitive data masking)
       ├── Formatter (structured + colored)
       └── Module Loggers (rpa, api, database)
```

**数据流变化**：
```
旧：代码 → print/logging → console
新：代码 → loguru →
              ├→ File (rotation/compression)
              ├→ WebSocket → Frontend (real-time display)
              └── Console (colored output)
```

### 性能影响

- **内存增加**：日志缓存和 WebSocket 连接，预计增加 < 50MB
- **CPU 增加**：日志序列化和 WebSocket 推送，预计增加 < 5%
- **磁盘 I/O**：日志文件写入，通过异步处理最小化影响
- **网络带宽**：WebSocket 日志流，可通过级别控制和过滤优化

### 安全性影响

**提升**：
- ✅ 敏感信息自动过滤（密码、Token、Cookie）
- ✅ 审计日志完整性（用户操作、系统变更）
- ✅ 异常追踪和监控
- ✅ 日志文件访问控制（文件权限）

**风险**：
- ⚠️ 日志文件可能包含敏感信息，需要加密存储
- ⚠️ WebSocket 日志流需要认证，防止未授权访问
- ⚠️ 日志级别不当可能暴露系统内部信息

### 用户体验影响

**提升**：
- ✅ 前端实时查看日志，无需登录服务器
- ✅ 日志搜索和过滤功能
- ✅ 调试和问题定位更快速
- ✅ 系统运行状态可视化

**折衷**：
- ⚠️ 日志详细度增加可能影响性能（可通过级别控制）
- ⚠️ 日志文件占用磁盘空间（通过轮转和清理管理）

## Migration Strategy

1. **安装依赖**：确认 loguru 已安装，添加可选依赖
2. **创建日志配置**：实现统一日志管理器
3. **实现双输出**：文件持久化 + WebSocket 流
4. **添加中间件**：HTTP 请求日志、全局异常捕获
5. **替换现有日志**：逐步替换 print 和 logging 为 loguru
6. **创建前端组件**：日志查看器和实时流
7. **测试验证**：日志完整性、性能影响、功能测试

## Success Criteria

- [ ] 所有模块使用统一的 logger（不再有 print 语句）
- [ ] 日志同时写入文件和发送到前端
- [ ] 日志文件自动轮转（按大小：100MB）和压缩
- [ ] 前端可以实时查看后端日志（WebSocket）
- [ ] 支持按模块、级别、关键词过滤日志
- [ ] 敏感信息（密码、Token）自动过滤
- [ ] 日志文件存储在 `backend/logs/` 目录
- [ ] 日志保留时间可配置（默认 30 天）
- [ ] 支持 JSON 格式结构化日志（可选启用）
- [ ] 性能影响 < 5% CPU 和 < 50MB 内存
- [ ] RPA 关键操作（登录、投递、聊天）有详细日志
