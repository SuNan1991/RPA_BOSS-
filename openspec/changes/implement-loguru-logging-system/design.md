# Design: Industrial-Grade Logging System with Loguru

## Context

### Current State

**后端日志现状**：
- Python logging 模块使用不统一，各模块独立配置
- 日志只输出到控制台，无持久化
- 大量使用 `print()` 语句进行调试，无法在生产环境控制
- RPA 操作（登录、投递、聊天）缺乏详细的过程记录
- 异常信息不完整，缺少上下文和堆栈追踪

**前端现状**：
- 无日志查看功能
- 调试需要登录服务器查看控制台输出
- 无法实时了解后端运行状态

**现有日志相关代码**：
- `backend/app/core/logging.py` - 使用标准 logging 模块
- `backend/app/core/config.py` - 包含日志配置项
- `pyproject.toml` - loguru 已列为依赖但未使用

### Constraints

**技术约束**：
- 必须使用 loguru 作为日志框架（已在依赖中）
- 必须保持与现有 FastAPI、WebSocket 架构兼容
- 日志文件存储在 `backend/logs/` 目录
- 必须支持日志轮转和压缩，防止磁盘占满
- 必须支持敏感信息过滤（密码、Token、Cookie）

**性能约束**：
- 日志写入不能阻塞主线程
- WebSocket 推送不能影响业务性能
- 日志文件 I/O 必须异步处理
- CPU 开销 < 5%，内存开销 < 50MB

**安全约束**：
- 日志文件权限设置为 640（owner rw, group r）
- WebSocket 日志流需要认证
- 敏感信息必须在写入前过滤

**设计约束**：
- 模块化设计，每个模块独立配置日志级别
- 支持动态调整日志级别（无需重启）
- 支持多种输出格式（文本、JSON）

### Stakeholders

**主要用户**：
- 开发人员：需要详细的调试日志，快速定位问题
- 运维人员：需要监控系统运行状态，查看错误日志
- 测试人员：需要重现问题依据，查看操作流程

**技术团队**：
- 后端开发者：需要统一的日志 API，易于集成
- 前端开发者：需要实时日志流 API，易于展示

## Goals / Non-Goals

### Goals

1. **统一日志管理**：使用 loguru 替换所有 print 和 logging，提供统一的 logger API
2. **双输出机制**：日志同时写入文件和推送到前端 WebSocket
3. **文件持久化**：自动轮转、压缩、清理过期日志
4. **实时监控**：前端通过 WebSocket 实时查看后端日志
5. **结构化日志**：支持 JSON 格式输出，便于日志分析
6. **模块化配置**：每个模块独立配置日志级别和格式
7. **性能优化**：异步日志写入，不阻塞业务逻辑
8. **敏感信息保护**：自动过滤密码、Token 等敏感字段

### Non-Goals

- ~~实现日志分析前端~~（日志存储为 JSON，可用 ELK/Loki 分析）
- ~~实现分布式日志追踪~~（单应用暂不需要 OpenTelemetry）
- ~~实现日志告警系统~~（后续可基于日志关键字实现）
- ~~实现日志审计报告~~（审计日志已存储，可单独生成报告）

## Decisions

### 1. 日志框架：loguru vs standard logging

**决策**：使用 loguru 替换 standard logging

**理由**：
- ✅ **开箱即用**：loguru 无需复杂配置，自带彩色输出、格式化
- ✅ **更好的异常处理**：自动记录完整的堆栈追踪和变量值
- ✅ **更容易集成**：一个 `import logger` 就能使用
- ✅ **更好的性能**：优化的日志写入，异步处理支持
- ✅ **功能丰富**：内置 rotation、compression、过滤等功能

**替代方案考虑**：
- **standard logging**：配置复杂，需要大量样板代码
- **structlog**：功能强大但配置繁琐，学习成本高

**权衡**：
- ⚠️ loguru 是第三方依赖（但已在 pyproject.toml 中）
- ⚠️ 团队需要熟悉新的 API（但 API 更简单）

### 2. 日志架构：集中式管理器 vs 分散式 logger

**决策**：集中式管理器 + 分散式 logger

**理由**：
- ✅ **统一配置**：通过管理器统一配置所有 logger
- ✅ **模块独立**：每个模块有独立 logger，可单独配置级别
- ✅ **易于维护**：修改日志行为只需调整管理器

**架构设计**：
```python
# backend/app/core/logging.py
class LogManager:
    """集中式日志管理器"""

    @staticmethod
    def get_logger(name: str):
        """获取模块 logger"""
        return logger.bind(module=name)

    @staticmethod
    def setup():
        """初始化全局 logger 配置"""
        logger.remove()  # 删除默认 handler
        # 添加文件 handler
        # 添加 WebSocket handler
        # 添加过滤器和格式化器

# 使用示例
from app.core.logging import LogManager
logger = LogManager.get_logger(__name__)  # 自动绑定模块名
logger.info("Message")  # 自动注入模块名、时间戳等上下文
```

**替代方案考虑**：
- **完全分散式**：每个模块独立创建 logger - 难以维护和配置
- **单一全局 logger**：所有模块共用一个 logger - 无法单独控制级别

**权衡**：
- 需要额外实现 LogManager 类
- 但提供了最佳的可维护性和灵活性

### 3. 日志持久化：文件轮转策略

**决策**：按大小和时间双策略轮转

**理由**：
- ✅ **防止文件过大**：单个文件超过 100MB 自动轮转
- ✅ **定期清理**：每天自动创建新文件，便于按日期查找
- ✅ **节省空间**：自动压缩过期日志（.gz 格式）
- ✅ **保留策略**：可配置保留天数（默认 30 天）

**实现方案**：
```python
from loguru import logger

logger.add(
    "logs/app_{time}.log",
    rotation="100 MB",  # 文件大小超过 100MB 时轮转
    retention="30 days",  # 保留 30 天
    compression="zip",  # 压缩旧日志
    enqueue=True,  # 异步写入，不阻塞主线程
    level="INFO"
)
```

**替代方案考虑**：
- **仅按大小轮转**：无法按日期组织日志
- **仅按时间轮转**：单个文件可能过大

**权衡**：
- 双策略可能产生较多小文件
- 但提供了最佳的查找和归档体验

### 4. WebSocket 日志流：自定义 Handler vs loguru 扩展

**决策**：实现自定义 loguru Handler

**理由**：
- ✅ **原生集成**：loguru 支持自定义 handler
- ✅ **异步发送**：通过 WebSocket 异步推送日志
- ✅ **级别控制**：可配置推送的日志级别
- ✅ **性能优化**：批量发送，减少 WebSocket 消息数量

**实现方案**：
```python
class WebSocketHandler:
    """自定义 WebSocket 日志 handler"""

    def __init__(self, connection_manager):
        self.connection_manager = connection_manager
        self.buffer = []
        self.buffer_size = 100  # 批量发送

    def write(self, message):
        """缓存日志消息"""
        self.buffer.append(message)
        if len(self.buffer) >= self.buffer_size:
            self.flush()

    def flush(self):
        """批量发送日志到前端"""
        if self.buffer:
            self.connection_manager.broadcast_logs(self.buffer)
            self.buffer = []
```

**替代方案考虑**：
- **在 API 中直接发送日志**：耦合度高，难以复用
- **使用消息队列**：增加复杂度，单应用不必要

**权衡**：
- 需要实现自定义 handler
- 但提供了最佳的解耦和性能

### 5. 敏感信息过滤：中间件 vs 装饰器 vs formatter

**决策**：使用 loguru filter function

**理由**：
- ✅ **灵活**：filter function 可以检查和修改每条日志
- ✅ **高效**：在日志写入前过滤，不消耗 I/O
- ✅ **可配置**：通过配置文件定义敏感字段

**实现方案**：
```python
SENSITIVE_FIELDS = ["password", "token", "cookie", "secret"]

def sensitive_data_filter(record):
    """过滤敏感信息"""
    message = record["message"]
    for field in SENSITIVE_FIELDS:
        # 替换敏感字段值为 ***
        message = re.sub(f'{field}=[^\\s]+', f'{field}=***', message)
    record["message"] = message
    return record

logger.add(..., filter=sensitive_data_filter)
```

**替代方案考虑**：
- **中间件**：无法拦截日志内部内容
- **装饰器**：需要包装每个日志调用，不现实

**权衡**：
- 正则表达式可能无法覆盖所有情况
- 但可覆盖大部分敏感信息，且性能好

### 6. 日志级别管理：动态调整 vs 配置文件

**决策**：配置文件 + API 动态调整

**理由**：
- ✅ **持久化**：配置文件保存在文件系统，重启后保持
- ✅ **灵活性**：API 允许运行时调整，无需重启
- ✅ **分级控制**：支持全局级别和模块级别

**实现方案**：
```python
# config/logging_config.yaml
loggers:
  default: INFO
  rpa: DEBUG
  api: INFO
  database: WARNING

# API 调整
@router.put("/api/log/level")
async def set_log_level(module: str, level: str):
    log_manager.set_level(module, level)
```

**替代方案考虑**：
- **仅配置文件**：需要重启应用才能生效
- **仅 API**：重启后丢失配置

**权衡**：
- 增加了配置管理复杂度
- 但提供了生产环境所需的灵活性

## Risks / Trade-offs

### Risk 1: WebSocket 日志流性能瓶颈

**描述**：大量日志实时推送可能导致 WebSocket 连接拥塞，影响业务性能。

**缓解措施**：
- ✅ 实现日志级别过滤，只推送重要日志（WARNING、ERROR）
- ✅ 使用批量发送（buffer_size=100），减少 WebSocket 消息数量
- ✅ 添加限流机制，每秒最多推送 100 条日志
- ✅ 前端实现日志缓存和分页显示
- ✅ 支持禁用实时日志流，仅查看文件日志

### Risk 2: 日志文件磁盘占满

**描述**：日志文件无限增长，导致磁盘空间不足。

**缓解措施**：
- ✅ 自动轮转（100MB）和压缩（zip）
- ✅ 自动清理 30 天前的日志
- ✅ 监控磁盘空间，低于 1GB 时告警
- ✅ 配置文件可自定义保留策略
- ✅ 支持完全禁用文件日志（仅控制台输出）

### Risk 3: 敏感信息泄露

**描述**：日志中可能包含用户密码、Token 等敏感信息。

**缓解措施**：
- ✅ 实现敏感字段自动过滤（password、token、cookie、secret）
- ✅ 对日志文件设置权限 640（owner rw, group r）
- ✅ 生产环境禁用 DEBUG 级别日志
- ✅ 定期审计日志内容，确保无敏感信息
- ✅ 记录谁访问了日志文件（文件访问日志）

### Risk 4: 异步日志丢失

**描述**：应用崩溃时，缓冲区中的日志可能丢失。

**缓解措施**：
- ✅ 使用 `enqueue=True` 异步写入，loguru 会优雅关闭
- ✅ 应用关闭时显式调用 logger.complete() 确保日志刷新
- ✅ 关键操作（错误、异常）使用同步模式确保写入
- ✅ 定期刷新缓冲区（每 10 秒）

### Risk 5: 性能影响

**描述**：日志记录可能影响应用性能，特别是高频操作。

**缓解措施**：
- ✅ 使用异步写入（enqueue=True），不阻塞主线程
- ✅ 生产环境使用 INFO 或 WARNING 级别，减少日志量
- ✅ RPA 操作日志使用独立 logger，可单独关闭
- ✅ 性能监控：记录日志耗时，超过 100ms 告警
- ✅ 支持完全禁用日志（极端情况）

### Risk 6: 前端日志显示性能

**描述**：大量日志实时渲染可能导致前端卡顿。

**缓解措施**：
- ✅ 使用虚拟滚动（仅渲染可见区域）
- ✅ 限制显示的日志数量（最多 1000 条）
- ✅ 实现日志分页加载
- ✅ 支持日志过滤和搜索，减少显示数量
- ✅ 使用防抖（debounce）减少渲染频率

## Migration Plan

### 阶段 1：基础设施搭建（Day 1-2）

1. **创建日志管理器**
   - 实现 `backend/app/core/logging.py`（LogManager 类）
   - 配置全局 logger（文件、控制台、WebSocket）
   - 实现敏感信息过滤器
   - 实现日志格式化器（文本、JSON）

2. **实现日志持久化**
   - 创建 `backend/logs/` 目录
   - 配置文件轮转和压缩
   - 配置日志清理策略

3. **实现 WebSocket 日志流**
   - 创建 WebSocket 日志 handler
   - 集成到现有 WebSocket 连接管理器
   - 实现批量发送和限流

### 阶段 2：后端集成（Day 2-3）

1. **替换现有日志**
   - 替换所有 `print()` 为 `logger.info()`
   - 替换标准 `logging` 为 loguru
   - 更新 `backend/app/core/logging.py` 中的日志配置

2. **添加中间件**
   - 创建 HTTP 请求日志中间件
   - 创建全局异常捕获中间件
   - 集成到 FastAPI 应用

3. **模块化 logger**
   - 为每个 RPA 模块创建独立 logger
   - 为 API、数据库创建独立 logger
   - 配置模块级别日志级别

### 阶段 3：前端集成（Day 3-4）

1. **创建日志 API**
   - GET /api/logs - 查询历史日志
   - PUT /api/logs/level - 调整日志级别
   - WebSocket /ws/logs - 实时日志流

2. **创建日志查看器组件**
   - `LogViewer.vue` - 日志列表和过滤
   - 实时日志流显示
   - 日志搜索和高亮
   - 日志导出功能

3. **集成到现有页面**
   - 在 AuthenticatedPage 添加日志入口
   - 创建日志管理页面（可选）

### 阶段 4：测试和优化（Day 4-5）

1. **功能测试**
   - 测试日志文件创建、轮转、压缩
   - 测试 WebSocket 日志流
   - 测试日志级别动态调整
   - 测试敏感信息过滤

2. **性能测试**
   - 测试高频日志场景（1000 条/秒）
   - 测试日志对 RPA 操作的影响
   - 测试 WebSocket 推送性能
   - 测试前端渲染性能

3. **安全测试**
   - 验证敏感信息过滤
   - 验证日志文件权限
   - 验证 WebSocket 认证

### 部署步骤

1. **备份现有代码**（如需回滚）
   ```bash
   git add .
   git commit -m "backup before implementing loguru logging"
   ```

2. **安装依赖**（如需新增）
   ```bash
   cd backend
   uv add python-json-logger  # 可选，JSON 序列化
   ```

3. **创建日志配置文件**
   ```bash
   mkdir -p backend/config
   cp logging_config.yaml.example backend/config/logging_config.yaml
   ```

4. **部署代码**
   ```bash
   # 按照 Migration Plan 的顺序部署
   # 每个阶段完成后测试验证
   ```

5. **监控日志系统**
   - 检查日志文件是否正常创建
   - 检查 WebSocket 推送是否正常
   - 监控磁盘空间和性能指标

### 回滚策略

如果出现严重问题：

1. **快速回滚**（15 分钟内）
   ```bash
   git revert HEAD
   git revert HEAD~1
   # ... 根据需要回滚多个 commit
   uv run python -m app.main
   ```

2. **部分回滚**
   - 保留日志基础设施，回滚到部分模块使用旧日志
   - 禁用问题功能（如 WebSocket 日志流）
   - 降级日志级别

3. **配置调整**
   - 将日志级别设置为 WARNING 或 ERROR
   - 禁用实时日志流
   - 减少日志轮转频率

## Open Questions

### Q1: WebSocket 日志流是否需要持久化？

**背景**：前端连接断开后重新连接，是否需要发送历史日志？

**当前倾向**：不发送历史日志
- ✅ 历史日志可通过 API 查询
- ✅ WebSocket 仅推送新产生的日志
- ✅ 减少首次连接的数据传输量

**需要决策**：是否提供"回放最近 N 条日志"功能？

### Q2: RPA 操作日志的详细程度？

**背景**：RPA 操作（登录、投递、聊天）可能产生大量日志。

**当前倾向**：使用独立 logger，默认 INFO 级别
- DEBUG：记录每个步骤和页面元素
- INFO：记录关键操作（开始、成功、失败）
- WARNING：记录重试和降级行为
- ERROR：记录异常和失败

**需要决策**：是否需要更细粒度的控制（如按功能模块分文件）？

### Q3: 日志文件是否需要加密？

**背景**：日志文件可能包含敏感信息，需要考虑存储安全。

**当前倾向**：不加密，但采取其他安全措施
- ✅ 文件权限 600（仅 owner 可写）
- ✅ 敏感信息过滤
- ✅ 定期审计和清理
- ⚠️ 如果需要更高安全性，考虑文件系统加密

**需要决策**：生产环境是否有日志加密的合规要求？

### Q4: JSON 格式日志是否默认启用？

**背景**：JSON 格式便于日志分析，但可读性差。

**当前倾向**：默认文本格式，可选 JSON
- ✅ 文本格式便于人工阅读和调试
- ✅ JSON 格式可通过配置启用
- ✅ 支持 A/B 两种格式同时输出

**需要决策**：是否在某些环境（如生产）强制使用 JSON 格式？

## Appendix

### A. 技术栈总览

**后端日志**：
- loguru 0.7.0+ - 核心日志框架
- python-json-logger (可选) - JSON 序列化
- FastAPI - WebSocket 推送
- aiosqlite - 日志存储（可选）

**前端日志展示**：
- Vue 3 + Composition API
- WebSocket - 实时日志流
- Tailwind CSS - 样式
- 虚拟滚动 - 大量日志渲染

### B. 日志级别定义

```python
# 标准 loguru 级别
TRACE (5) - 最详细的诊断信息
DEBUG (10) - 开发和调试信息
INFO (20) - 一般信息（默认）
SUCCESS (25) - 成功操作
WARNING (30) - 警告信息
ERROR (40) - 错误信息
CRITICAL (50) - 严重错误
```

**推荐配置**：
- 开发环境：DEBUG
- 测试环境：INFO
- 生产环境：WARNING

### C. 日志文件结构

```
backend/logs/
├── app_2025-02-07.log        # 当前日志文件
├── app_2025-02-06.log.gz     # 已压缩的日志
├── app_2025-02-05.log.gz
├── app_2025-02-04.log.gz
└── ... (保留 30 天)
```

**命名规范**：
- `{application}_{date}.log` - 正常日志
- `{application}_{date}.log.gz` - 压缩日志
- `{application}_error_{date}.log` - 错误日志（可选）

### D. 性能优化策略

1. **异步写入**：使用 `enqueue=True`，日志写入不阻塞主线程
2. **批量发送**：WebSocket 每批发送 100 条日志
3. **级别过滤**：生产环境使用 WARNING 及以上级别
4. **缓冲刷新**：每 10 秒刷新一次缓冲区
5. **前端虚拟滚动**：仅渲染可见日志行
6. **前端分页**：每次加载 100-500 条日志

### E. 参考资源

- **loguru 文档**：https://github.com/Delgan/loguru
- **FastAPI WebSocket**：https://fastapi.tiangolo.com/advanced/websockets/
- **Python JSON Logger**：https://github.com/niedbalski/python-json-logger
- **ELK Stack**：https://www.elastic.co/what-is/elk-stack
