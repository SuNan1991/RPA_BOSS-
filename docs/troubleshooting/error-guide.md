# Claude Code 错误预防指南

> **目的**: 记录本次实现中遇到的错误及其预防措施，避免未来重复犯错

## 🚨 关键错误案例

### 错误 #1: 模块导入路径错误 (Import Path Mistakes)

**错误现象**:
```python
ImportError: cannot import name 'AccountService' from 'app.services'
ModuleNotFoundError: No module named 'backend'
```

**根本原因**:
1. 创建新文件时覆盖了现有的 `__init__.py`，删除了原有的导入语句
2. 使用了绝对导入 `from backend.rpa.modules...` 但在运行时 `backend` 不在 Python 路径中
3. Python 的模块搜索路径与项目目录结构不匹配

**预防措施**:
```python
# ❌ 错误做法
from backend.rpa.modules.browser_manager import BrowserManager  # backend 可能不在路径中

# ✅ 正确做法（在 app/ 包内部）
from rpa.modules.browser_manager import BrowserManager  # 相对于项目根目录

# ✅ 或者使用 sys.path 确保路径正确
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from rpa.modules.browser_manager import BrowserManager
```

**检查清单**:
- [ ] 创建新 `__init__.py` 时，先读取现有内容
- [ ] 保留所有现有的导入语句
- [ ] 添加新的导入，而不是替换
- [ ] 测试导入是否正常工作
- [ ] 使用 `python -c "import module"` 验证

---

### 错误 #2: 异步/同步数据库混用 (Async/Sync Database Mixing)

**错误现象**:
```python
# 代码中使用同步数据库调用
db = get_db()
cursor = db.cursor()
cursor.execute('SELECT ...')

# 但实际数据库是 aiosqlite (异步)
class Database:
    async def get_connection(self) -> aiosqlite.Connection:
```

**根本原因**:
1. 没有检查现有数据库的 API 类型
2. 假设数据库是同步的，但实际是异步的
3. 新代码风格与现有代码风格不一致

**预防措施**:
```python
# ✅ 步骤 1: 先检查现有数据库 API
# 读取 backend/app/core/database.py
# 确认是 aiosqlite (异步) 还是 sqlite3 (同步)

# ✅ 步骤 2: 如果是异步数据库
import aiosqlite

async def save_session(self):
    conn = await self._get_db()  # 异步获取连接
    try:
        await conn.execute('...')  # 使用 await
        await conn.commit()
    finally:
        await conn.close()  # 异步关闭

# ✅ 步骤 3: 如果是同步数据库
def save_session(self):
    conn = self._get_db()
    cursor = conn.cursor()
    cursor.execute('...')
    conn.commit()
```

**检查清单**:
- [ ] 在编写数据库代码前，先读取 `backend/app/core/database.py`
- [ ] 确认是 `aiosqlite` (异步) 还是 `sqlite3` (同步)
- [ ] 异步数据库: 所有调用都要加 `await`
- [ ] 同步数据库: 使用 `cursor.execute()` 不需要 `await`
- [ ] 保持与现有代码风格一致

---

### 错误 #3: 懒加载导致的模块属性访问问题

**错误现象**:
```python
class RPAService:
    @property
    def browser_manager(self):
        # 动态加载模块
        # 但后续代码假设它总是可用的
```

**根本原因**:
1. 使用 `@property` 延迟加载导致每次访问都重新导入
2. 模块路径计算错误
3. 没有缓存导入的模块

**预防措施**:
```python
# ❌ 错误做法
class RPAService:
    @property
    def browser_manager(self):
        # 每次访问都重新导入 - 性能差且容易出错
        spec = importlib.util.spec_from_file_location(...)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.BrowserManager()

# ✅ 正确做法 1: 直接导入（推荐）
from rpa.modules.browser_manager import BrowserManager

class RPAService:
    def __init__(self):
        self.browser_manager = BrowserManager()

# ✅ 正确做法 2: 如果必须延迟加载，使用缓存
class RPAService:
    def __init__(self):
        self._browser_manager = None

    @property
    def browser_manager(self):
        if self._browser_manager is None:
            from rpa.modules.browser_manager import BrowserManager
            self._browser_manager = BrowserManager()
        return self._browser_manager
```

---

### 错误 #4: __init__.py 不当修改

**错误现象**:
```python
# 原来的 backend/app/services/__init__.py
"""Services"""
from .account_service import AccountService
from .job_service import JobService
from .task_service import TaskService

# 被错误地替换为
"""Services"""  # ❌ 所有导入丢失了！
```

**根本原因**:
1. 使用 `echo` 或简单的 Write 工具覆盖文件
2. 没有先读取现有内容
3. 没有保留现有导出

**预防措施**:
```bash
# ❌ 错误做法
echo '"""Services"""' > backend/app/services/__init__.py

# ✅ 正确做法 1: 先读取，再编辑
# 使用 Read 工具读取文件
# 使用 Edit 工具添加新内容

# ✅ 正确做法 2: 追加内容
echo 'from .new_module import NewService' >> backend/app/services/__init__.py

# ✅ 正确做法 3: Python 脚本更新
python3 << 'EOF'
with open('backend/app/services/__init__.py', 'r') as f:
    content = f.read()

# 添加新的导入
if 'NewService' not in content:
    content += '\nfrom .new_module import NewService'

with open('backend/app/services/__init__.py', 'w') as f:
    f.write(content)
EOF
```

**检查清单**:
- [ ] 修改 `__init__.py` 前，先用 Read 工具读取
- [ ] 保留所有现有的导入和导出
- [ ] 添加新导入，而不是替换
- [ ] 更新 `__all__` 列表（如果存在）
- [ ] 测试导入是否正常

---

### 错误 #5: 数据库迁移路径错误

**错误现象**:
```python
# 代码中的路径
migration_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'migrations')
# 实际路径解析错误
FileNotFoundError: [Errno 2] No such file or directory: '...\\app\\rpa\\modules'
```

**根本原因**:
1. 使用相对路径 `..` 计算容易出错
2. `__file__` 在不同运行方式下路径不同
3. 没有使用绝对路径

**预防措施**:
```python
# ❌ 错误做法
migration_dir = os.path.join(
    os.path.dirname(__file__),  # backend/app/services
    '..', '..',
    'migrations'
)
# 结果: backend/app/../../migrations = 基于运行目录

# ✅ 正确做法 1: 从项目根目录计算
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
migration_dir = os.path.join(PROJECT_ROOT, 'backend', 'migrations')

# ✅ 正确做法 2: 使用 pathlib
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent.parent
migration_dir = PROJECT_ROOT / 'backend' / 'migrations'

# ✅ 正确做法 3: 配置文件中定义路径
# config.py
BASE_DIR = Path(__file__).parent.parent
MIGRATIONS_DIR = BASE_DIR / 'migrations'
```

**检查清单**:
- [ ] 优先使用绝对路径
- [ ] 使用 `pathlib` 代替 `os.path`
- [ ] 在配置文件中定义关键路径
- [ ] 打印路径进行调试: `print(f"Path: {path}, exists: {path.exists()}")`

---

## 🛡️ 通用编码规范

### 1. 文件修改规范

**修改现有文件前**:
```python
# ✅ 步骤 1: 读取现有内容
with open('file.py', 'r') as f:
    content = f.read()

# ✅ 步骤 2: 理解现有逻辑
# 检查导入、类定义、函数签名

# ✅ 步骤 3: 添加新内容（不删除现有内容）
with open('file.py', 'a') as f:
    f.write('\n# New content\n')

# ✅ 步骤 4: 测试
import subprocess
subprocess.run(['python', '-m', 'py_compile', 'file.py'])
```

### 2. 导入语句规范

**优先级**:
1. 标准库 (`import os`, `import sys`)
2. 第三方库 (`import fastapi`)
3. 项目内部导入 (`from app.core import config`)

**格式**:
```python
# ✅ 正确
import os
import sys
from typing import Optional

from fastapi import APIRouter
from cryptography.fernet import Fernet

from app.core.config import settings
from app.services import AccountService

# ❌ 错误
import os, sys
from app.core.config import *
```

### 3. 异步编程规范

```python
# ✅ 数据库操作全部异步
import aiosqlite

async def get_data():
    async with aiosqlite.connect('db.sqlite') as db:
        cursor = await db.execute('SELECT ...')
        rows = await cursor.fetchall()
        return rows

# ❌ 混用异步和同步
async def get_data():
    db = sqlite3.connect('db.sqlite')  # 同步！
    cursor = db.execute('SELECT ...')  # 同步！
```

### 4. 路径处理规范

```python
# ✅ 使用 pathlib
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
config_path = BASE_DIR / 'config' / 'settings.yaml'

# ❌ 使用 os.path + 相对路径
import os
config_path = os.path.join('..', 'config', 'settings.yaml')
```

---

## 📋 修改文件检查清单

在修改任何 `__init__.py` 文件前，检查：

- [ ] 使用 Read 工具读取现有内容
- [ ] 记录所有现有的导入语句
- [ ] 记录所有现有的 `__all__` 导出
- [ ] 保留现有内容，添加新内容
- [ ] 更新 `__all__` 列表（如果存在）
- [ ] 运行 `python -c "import package"` 测试

在创建数据库相关代码前，检查：

- [ ] 读取 `backend/app/core/database.py`
- [ ] 确认是 aiosqlite (异步) 还是 sqlite3 (同步)
- [ ] 检查现有数据库操作的风格
- [ ] 遵循相同的模式（同步/异步）
- [ ] 使用相同的连接方式

在使用导入前，检查：

- [ ] 确认模块在 Python 路径中
- [ ] 测试导入: `python -c "import module"`
- [ ] 使用正确的导入方式（相对 vs 绝对）
- [ ] 避免循环导入
- [ ] 使用类型注解避免 IDE 警告

---

## 🎯 快速决策树

**问题**: 我需要导入一个模块

```
是从当前包导入？
├─ 是 → 使用相对导入: from .module import Class
└─ 否 → 模块在项目根目录下？
    ├─ 是 → 使用绝对导入: from package.module import Class
    └─ 否 → 添加到 sys.path 或修改项目结构
```

**问题**: 我需要修改 `__init__.py`

```
文件已存在？
├─ 是 → 先读取现有内容 → 追加新导入 → 测试
└─ 否 → 创建新文件 → 添加导入
```

**问题**: 我需要访问数据库

```
检查 database.py
├─ aiosqlite (异步) → 所有操作加 await
├─ sqlite3 (同步) → 正常调用
└─ SQLAlchemy → 检查是 sync 还是 async session
```

---

## 🔧 调试工具

### 快速验证导入
```bash
# 验证模块可导入
python -c "from backend.app.services import AccountService"

# 验证路径
python -c "import os; print(os.path.abspath('.'))"

# 验证 Python 路径
python -c "import sys; print('\n'.join(sys.path))"
```

### 快速验证文件修改
```bash
# 检查文件是否存在
ls -la backend/app/services/__init__.py

# 检查文件内容
cat backend/app/services/__init__.py

# 检查 Python 语法
python -m py_compile backend/app/services/__init__.py
```

---

## 📝 总结

**三大原则**:
1. **先读取，后修改** - 任何文件修改前先读取
2. **保持一致性** - 与现有代码风格保持一致
3. **测试验证** - 修改后立即测试

**五个关键检查点**:
1. 导入路径是否正确？
2. 异步/同步是否匹配？
3. `__init__.py` 是否保留了现有导入？
4. 文件路径是否使用绝对路径？
5. 是否与现有代码风格一致？

**记住**: 这些错误都源于"没有仔细检查现有代码"。在添加新功能前，花 5 分钟阅读相关文件，可以节省数小时的调试时间。
