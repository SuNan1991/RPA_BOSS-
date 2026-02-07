# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

BOSS直聘自动化招聘系统 (BOSS Zhipin Automated Recruitment System) - An RPA system built with DrissionPage + FastAPI + Vue 3 that automates job search, application, and chat features on the BOSS Zhipin platform.

**Recent Major Change**: Migrated from MongoDB to SQLite (Feb 2026). All database operations now use aiosqlite (async), IDs changed from string to integer. See `DEPLOYMENT.md` for migration details.

## Essential Commands

### Backend Development

```bash
# Start backend (from project root)
cd backend
python -m app.main

# Using uv (recommended)
uv run python -m app.main

# Install dependencies
uv sync                    # uv
pip install -r requirements.txt  # pip

# Add new dependency
uv add package-name
uv add --dev package-name     # dev dependency

# Run tests
pytest                      # run all tests
pytest tests/test_specific.py -v  # specific test

# Code quality
ruff check .                # lint
ruff check . --fix          # lint + auto-fix
ruff format .               # format
black .                     # alternative formatter
mypy app/                   # type checking
pre-commit run --all-files  # run all pre-commit hooks
```

### Frontend Development

```bash
# Start frontend dev server
cd frontend
npm run dev                 # Vite dev server on :5173

# Build for production
npm run build               # builds to dist/

# Preview production build
npm run preview

# Linting
npm run lint                # ESLint with auto-fix
```

### Full Stack Development

```bash
# Start both backend and frontend
start.bat                   # Windows script that starts both

# Or manually in separate terminals:
# Terminal 1:
cd backend && python -m app.main
# Terminal 2:
cd frontend && npm run dev
```

### Database Operations

```bash
# Backup database (SQLite is a single file)
cp backend/data/boss_rpa.db backend/data/boss_rpa.db.backup

# Query database directly
sqlite3 backend/data/boss_rpa.db
> .tables                    # list tables
> SELECT * FROM accounts LIMIT 10;
> .quit

# Run migrations (happens automatically on startup)
# Migration files are in backend/migrations/
```

## Architecture & Code Organization

### Backend Architecture (FastAPI + SQLite)

**Key Pattern**: Async all the way down. The database layer uses `aiosqlite`, so ALL database operations must be async (use `await`).

```
backend/
├── app/                        # FastAPI application
│   ├── api/                   # API route handlers (thin layer)
│   ├── core/                  # Configuration, database, logging
│   │   ├── database.py        # aiosqlite wrapper - async only!
│   │   └── config.py          # Settings from env/pydantic
│   ├── services/              # Business logic layer
│   │   ├── account_service.py
│   │   ├── job_service.py
│   │   └── rpa_service.py     # NEW: RPA orchestration
│   ├── schemas/               # Pydantic models
│   └── main.py                # App entry point, runs migrations
│
├── rpa/                       # RPA automation modules
│   ├── core/                  # Base classes, browser management
│   │   ├── base.py           # BaseModule abstract class
│   │   └── browser.py        # Existing browser manager
│   └── modules/               # Feature modules
│       ├── browser_manager.py # NEW: Singleton browser for login
│       ├── anti_detection.py  # NEW: Anti-bot-detection config
│       ├── session_manager.py # NEW: Session persistence (async)
│       ├── captcha/           # Verification code handling
│       ├── login/             # BOSS login flow
│       ├── job/               # Job search
│       └── chat/              # Auto chat
│
├── data/                      # SQLite database files
│   └── boss_rpa.db           # Created automatically on first run
└── migrations/               # SQL migration files (run on startup)
```

**Critical Import Rules** (see `CLAUDE_ERROR_GUIDE.md` for details):
- ✅ Use relative imports from `backend/`: `from rpa.modules.browser_manager import BrowserManager`
- ✅ DO NOT use `from backend.rpa...` - will fail at runtime
- ✅ All database access is async via aiosqlite
- ✅ When modifying `__init__.py`, READ FIRST, then ADD (don't replace)

**Request Flow**:
```
HTTP Request → API Route (app/api/) → Service Layer (app/services/) → RPA Module (rpa/modules/) → Database (aiosqlite)
```

**API Route Pattern**:
```python
# backend/app/api/accounts.py
from fastapi import APIRouter
from ..services import AccountService
from ..core.database import get_database  # async dependency injection

router = APIRouter(prefix="/api/accounts", tags=["accounts"])

@router.get("/")
async def list_accounts():
    """Use async for database access"""
    conn = await get_database()
    cursor = await conn.execute("SELECT ...")
    rows = await cursor.fetchall()
    return rows
```

**RPA Module Pattern**:
```python
# rpa/modules/some_module.py
from rpa.core.base import BaseModule
from rpa.core.browser import browser_manager

class SomeModule(BaseModule):
    def __init__(self):
        super().__init__()
        self.browser = browser_manager

    def execute(self, **kwargs):
        # RPA automation logic here
        result = self.browser.some_action()
        return {"success": True, "data": result}
```

### Frontend Architecture (Vue 3 + Tailwind CSS)

**Recent Refactor**: Removed Element Plus, migrated to Tailwind CSS + Headless UI. Now has only 2 main views.

```
frontend/
├── src/
│   ├── components/            # Vue components
│   │   ├── Button.vue        # Reusable button variants
│   │   ├── StatusIndicator.vue
│   │   ├── LoadingSpinner.vue
│   │   ├── GlassCard.vue     # Glassmorphism wrapper
│   │   ├── LandingPage.vue   # Login page (unauthenticated)
│   │   ├── AuthenticatedPage.vue  # Dashboard (authenticated)
│   │   └── AccountCard.vue   # User info display
│   │
│   ├── stores/               # Pinia state management
│   │   ├── auth.ts           # Authentication state
│   │   ├── theme.ts          # Light/dark mode
│   │   └── rpa.ts            # RPA operation state
│   │
│   ├── composables/          # Reusable composition functions
│   │   ├── useAuth.ts        # login(), logout(), checkStatus()
│   │   ├── useRPA.ts         # RPA operations
│   │   ├── useTheme.ts       # Theme management
│   │   └── useWebSocket.ts   # WebSocket connection
│   │
│   ├── views/
│   │   └── Home.vue          # Single-page app entry point
│   │
│   ├── api/                  # API client (axios)
│   │   └── index.ts          # getStatus(), login(), logout()
│   │
│   ├── router/               # Simplified routing
│   │   └── index.ts          # Only one route: /
│   │
│   └── styles/
│       └── theme.css         # Tailwind + CSS variables
│
├── tailwind.config.js        # Tailwind configuration
├── postcss.config.js         # PostCSS + Tailwind
└── package.json
```

**Styling System**:
- **Primary Color**: `#5C6BC0` (indigo)
- **Design**: Glassmorphism (backdrop blur, semi-transparent backgrounds)
- **Theming**: CSS variables + `.dark` class for dark mode
- **Framework**: Tailwind CSS utility classes
- **Components**: Headless UI (unstyled, fully customizable)

**State Management Pattern**:
```typescript
// Store (Pinia) - holds state
const authStore = useAuthStore()
authStore.setAuth({ isAuthenticated: true, user: {...} })

// Composable - business logic
const { login, logout, loading } = useAuth()
await login()  // Calls API, updates store
```

**WebSocket Connection**:
- Endpoint: `ws://localhost:8000/api/auth/ws`
- Used for real-time login status updates
- Auto-reconnect with exponential backoff
- Heartbeat every 30 seconds

## Database Schema (SQLite)

**Tables**:
- `accounts` - BOSS accounts (id, phone, username, cookie_status, last_login)
- `jobs` - Searched job listings (id, job_name, company_name, salary, city, ...)
- `tasks` - Automation tasks (id, name, task_type, config, status, result)
- `sessions` - NEW: Login sessions (id, cookies [encrypted], user_info, expires_at)
- `login_logs` - NEW: Login attempts (id, username, success, failure_reason, timestamp)

**Important**: All ID fields are `INTEGER` (auto-increment), not strings. This changed during MongoDB → SQLite migration.

## Critical Implementation Details

### When Working with Database Code

1. **ALWAYS use async/await**:
   ```python
   # ✅ Correct
   async def get_data():
       conn = await get_database()
       cursor = await conn.execute("SELECT * FROM accounts")
       return await cursor.fetchall()

   # ❌ WRONG - will fail
   def get_data():
       conn = get_database()  # This returns a coroutine!
       cursor = conn.execute("SELECT * FROM accounts")
   ```

2. **Database connection is dependency-injected**:
   ```python
   # In API routes
   from app.core.database import get_database

   @router.get("/accounts")
   async def get_accounts():
       conn = await get_database()  # Get connection
       # ... use conn

   # In services
   from app.core.database import db
   # Or use async with aiosqlite.connect() directly
   ```

### When Modifying __init__.py Files

**READ THE FILE FIRST** - Never replace an existing `__init__.py` without reading it. This is the #1 cause of import errors.

```bash
# ✅ Correct workflow
# 1. Read the file to see existing imports
# 2. Add your new import to the list
# 3. Update __all__ if present
# 4. Test import with: python -c "import package"

# ❌ WRONG - This destroys existing imports
echo '"""New description"""' > backend/app/services/__init__.py
```

See `CLAUDE_ERROR_GUIDE.md` for full details on this common mistake.

### When Adding New RPA Modules

1. Inherit from `BaseModule`:
   ```python
   from rpa.core.base import BaseModule

   class NewFeatureModule(BaseModule):
       def execute(self, **kwargs):
           # Implementation
           return {"success": True}
   ```

2. Use the existing browser manager:
   ```python
   from rpa.core.browser import browser_manager

   # It's a singleton - get the instance
   browser = browser_manager.get_browser()
   ```

3. Add error handling and logging:
   ```python
   from app.core.logging import logger

   try:
       result = self.browser.some_action()
       logger.info(f"Action successful: {result}")
   except Exception as e:
       logger.error(f"Action failed: {e}")
       return {"success": False, "error": str(e)}
   ```

### When Adding Frontend Components

1. **Use Tailwind classes** for styling:
   ```vue
   <template>
     <div class="glass-card p-6 rounded-2xl">
       <button class="btn btn-primary">Click me</button>
     </div>
   </template>
   ```

2. **Add glassmorphism effect**:
   ```vue
   <template>
     <div class="glass">  <!-- defined in theme.css -->
       Content with backdrop blur
     </div>
   </template>
   ```

3. **Support dark mode**:
   ```vue
   <template>
     <div :class="{ 'dark': isDark }">
       <div class="bg-white dark:bg-gray-900">
         Adaptive content
       </div>
     </div>
   </template>
   ```

### Import Path Rules

**From backend code** (e.g., `backend/app/api/something.py`):
- To import from `backend/rpa/`: `from rpa.modules.browser_manager import BrowserManager`
- To import from `backend/app/`: `from app.services import AccountService`
- DO NOT use `from backend.rpa...` - the `backend` prefix is not in Python path when running

**From frontend code**:
- Use `@/` alias for `src/`: `import Button from '@/components/Button.vue'`
- Use `~` alias if configured for project root

## Testing Strategy

### Backend Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_account_service.py -v

# Run with coverage
pytest --cov=app --cov=rpa

# Run async tests specifically
pytest tests/test_async.py
```

### Frontend Tests

```bash
# Not currently implemented
# Add testing framework if needed (Vitest, Jest, etc.)
```

### Manual Testing Checklist

- [ ] Backend starts without errors: `python -m app.main`
- [ ] Health check responds: `curl http://localhost:8000/health`
- [ ] Frontend builds: `npm run build`
- [ ] Frontend dev server starts: `npm run dev`
- [ ] Database file created: `ls backend/data/boss_rpa.db`
- [ ] Can query database: `sqlite3 backend/data/boss_rpa.db ".tables"`

## Git Hooks & Code Quality

The project uses pre-commit hooks for code quality:

```bash
# Install hooks (one-time setup)
cd backend
pre-commit install --hook-type pre-commit --hook-type commit-msg --hook-type pre-push

# Run hooks manually
pre-commit run --all-files

# Update hook versions
pre-commit autoupdate
```

**Conventional Commits** format required:
```
type(scope): description

Examples:
feat(login): add phone verification support
fix(api): fix pagination bug in jobs endpoint
docs: update deployment guide
refactor(rpa): simplify browser management
```

Allowed types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`, `build`, `revert`

## Common Patterns

### Adding a New API Endpoint

1. Create route file in `backend/app/api/`
2. Define Pydantic schemas in `backend/app/schemas/`
3. Implement service logic in `backend/app/services/`
4. Register router in `backend/app/api/__init__.py`

### Adding a New Frontend Page

1. Create component in `frontend/src/components/` or `frontend/src/views/`
2. Add route in `frontend/src/router/index.ts` (if needed)
3. Add navigation/link to reach the page

### Handling Async Database Operations

```python
# Service layer example
class AccountService:
    async def get_account(self, account_id: int):
        """Always use async for database access"""
        from app.core.database import get_database

        conn = await get_database()
        cursor = await conn.execute(
            "SELECT * FROM accounts WHERE id = ?",
            (account_id,)
        )
        row = await cursor.fetchone()

        if row:
            # Convert row to dict/Pydantic model
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None
```

## Environment Variables

**Backend (.env)**:
```bash
APP_NAME=BOSS_RPA
DEBUG=True
SQLITE_DB_PATH=data/boss_rpa.db
SESSION_ENCRYPTION_KEY=<generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">
```

**Frontend**:
```bash
VITE_API_BASE_URL=http://localhost:8000
```

## Troubleshooting

### Import Error: "No module named 'backend'"

**Cause**: Using `from backend.rpa...` imports.

**Fix**: Change to relative import: `from rpa.modules...`

See `CLAUDE_ERROR_GUIDE.md` for detailed explanation.

### Database Locked Error

**Cause**: Multiple instances trying to write to SQLite.

**Fix**: Ensure only one backend instance is running. SQLite with WAL mode (enabled by default) handles multiple readers but serializes writes.

### Frontend Build Fails

**Common causes**:
1. TypeScript errors - check `vue-tsc` output
2. Missing imports - check import paths
3. Tailwind CSS syntax errors - check class names

**Debug**: Run `npm run build` and read error messages carefully.

## Related Documentation

- `CLAUDE_ERROR_GUIDE.md` - Detailed analysis of common errors and how to avoid them
- `README.md` - Project overview and setup instructions
- `DEPLOYMENT.md` - MongoDB to SQLite migration details
- `.pre-commit-config.yaml` - Git hooks configuration
