# Loguru 日志系统使用指南

## 快速启动

### 1. 启动后端（带日志系统）
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### 2. 启动前端
```bash
cd frontend
npm run dev
```

前端将运行在 http://localhost:5173/

## API 端点

### 查询日志
```bash
# 查询最近 100 条日志
curl http://localhost:8001/api/logs/

# 查询最近 50 条 ERROR 级别日志
curl "http://localhost:8001/api/logs/?limit=50&level=ERROR"

# 查询最近 6 小时的日志
curl "http://localhost:8001/api/logs/?hours=6"

# 搜索包含关键词的日志
curl "http://localhost:8001/api/logs/?keyword=login"

# 组合查询
curl "http://localhost:8001/api/logs/?level=ERROR&hours=24&keyword=failure&limit=20"
```

### 日志统计
```bash
curl http://localhost:8001/api/logs/stats
```

返回示例：
```json
{
  "connected_clients": 0,
  "buffer_size": 0,
  "logs_sent": 0,
  "log_file_count": 2,
  "log_file_size_bytes": 6040,
  "log_file_size_mb": 0.01
}
```

### 导出日志
```bash
# 导出为 JSON
curl -O http://localhost:8001/api/logs/export?format=json&hours=24

# 导出为 CSV
curl -O http://localhost:8001/api/logs/export?format=csv&hours=24
```

### 动态调整日志级别
```bash
# 设置全局日志级别为 DEBUG
curl -X PUT http://localhost:8001/api/logs/level/global -H "Content-Type: application/json" -d '{"level":"DEBUG"}'

# 设置特定模块的日志级别
curl -X PUT http://localhost:8001/api/logs/level/app.main -H "Content-Type: application/json" -d '{"level":"TRACE"}'
```

可用级别：TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL

### 清理旧日志
```bash
# 删除 30 天前的日志
curl -X POST "http://localhost:8001/api/logs/cleanup?days=30"

# 删除 90 天前的日志
curl -X POST "http://localhost:8001/api/logs/cleanup?days=90"
```

## WebSocket 实时日志流

### 连接端点
```
ws://localhost:8001/ws/logs
```

### 消息格式

**连接确认**:
```json
{
  "type": "connected",
  "message": "WebSocket log stream connected",
  "timestamp": "2026-02-07T01:18:47.110"
}
```

**日志批次**:
```json
[
  {
    "timestamp": "2026-02-07 01:18:47.112",
    "level": "ERROR",
    "module": "app.main",
    "function_line": "lifespan:77",
    "message": "Error running migrations..."
  }
]
```

### 控制命令

**暂停接收**:
```
pause
```

**恢复接收**:
```
resume
```

**心跳检测**:
```
ping
```

响应：
```json
{
  "type": "pong",
  "timestamp": "2026-02-07T01:18:50.000"
}
```

## 日志文件位置

```
backend/logs/
├── app_2026-02-06.log          # 今天的所有日志
├── error_2026-02-06.log        # 今天的错误日志
├── app_2026-02-05.log.zip      # 昨天的日志（已压缩）
├── error_2026-02-05.log.zip    # 昨天的错误日志（已压缩）
└── archive/                    # 归档目录（自动创建）
```

## 在代码中使用日志

### 基本用法
```python
from app.core.logging import get_logger

logger = get_logger(__name__)

logger.info("用户登录成功")
logger.error("数据库连接失败", extra={"user_id": 123})
logger.success("任务执行完成")
```

### 不同级别
```python
logger.trace("最详细的跟踪信息")
logger.debug("调试信息")
logger.info("一般信息")
logger.success("成功操作")
logger.warning("警告信息")
logger.error("错误信息")
logger.critical("严重错误")
```

### 结构化日志
```python
logger.info("任务执行", extra={
    "task_id": 456,
    "duration": 123.45,
    "status": "completed"
})
```

### 异常日志
```python
try:
    1 / 0
except Exception as e:
    logger.error(f"计算失败: {e}")
    logger.exception("详细异常信息")  # 自动包含堆栈跟踪
```

## 前端使用

### LogViewer 组件

在 Vue 组件中使用：

```vue
<template>
  <LogViewer />
</template>

<script setup>
import LogViewer from '@/components/LogViewer.vue'
</script>
```

### 功能说明
- **实时模式**: 点击"🔴 实时"按钮开始接收实时日志
- **暂停模式**: 点击"▶️ 暂停"按钮停止接收
- **过滤**:
  - 按日志级别过滤
  - 按模块过滤
  - 按关键词搜索
  - 按时间范围过滤
- **导出**: 点击"导出"按钮下载日志文件
- **清空**: 点击"清空"按钮清除显示的日志
- **展开详情**: 点击日志条目查看详细信息（函数名、行号、异常堆栈）

## 配置说明

### 日志轮转
- **大小触发**: 单个文件达到 100MB 时自动轮转
- **时间触发**: 每天 00:00 自动创建新文件
- **压缩**: 轮转后的文件自动压缩为 .zip 格式

### 日志保留
- **app 日志**: 保留 30 天
- **error 日志**: 保留 90 天

### 敏感信息过滤
系统会自动过滤以下敏感信息：
- `password=***`
- `token=***`
- `cookie=***`
- `secret=***`
- `api_key=***`
- `authorization=Bearer ***`

## 故障排查

### 问题：日志文件未创建
**解决方案**:
1. 检查 backend/logs/ 目录是否存在
2. 确保有写入权限
3. 触发一个日志操作（如访问 API）

### 问题：WebSocket 无法连接
**解决方案**:
1. 确认后端正在运行
2. 检查防火墙设置
3. 确认使用正确的端口号（8001）

### 问题：日志级别调整不生效
**解决方案**:
1. 确认使用的是正确的模块名
2. 检查级别名称拼写（必须大写）
3. 查看后端日志确认是否有错误

### 问题：端口 8000 被占用
**解决方案**:
使用端口 8001 或其他可用端口：
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

## 性能优化建议

1. **生产环境**: 将日志级别设置为 INFO 或 WARNING
2. **开发环境**: 可以使用 DEBUG 级别
3. **高频日志**: 考虑使用采样或异步写入
4. **大文件查询**: 使用 hours 参数限制查询范围
5. **实时监控**: 仅在需要时启用 WebSocket 实时流

## 最佳实践

1. **使用合适的日志级别**
   - TRACE: 仅用于开发调试
   - DEBUG: 开发和测试
   - INFO: 正常业务流程
   - SUCCESS: 重要的成功操作
   - WARNING: 可恢复的异常情况
   - ERROR: 需要关注的错误
   - CRITICAL: 系统级严重错误

2. **记录有意义的消息**
   ```python
   # 好的做法
   logger.info("用户登录成功", extra={"user_id": user.id})

   # 不好的做法
   logger.info("登录")
   ```

3. **使用结构化数据**
   ```python
   logger.info("任务完成", extra={
       "task_id": task.id,
       "duration_ms": duration,
       "records_processed": count
   })
   ```

4. **避免记录敏感信息**
   - 系统会自动过滤常见敏感字段
   - 手动记录时注意不要包含密码、token 等

5. **定期清理旧日志**
   - 系统会自动清理
   - 可以手动触发清理以节省空间
