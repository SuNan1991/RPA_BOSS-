# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

## [1.1.0] - 2026-02-06

### ⚠️ BREAKING CHANGES

- **Database Migration**: Migrated from MongoDB to SQLite
  - Removed MongoDB dependency (motor, pymongo)
  - Added SQLite with aiosqlite driver
  - Changed ID type from MongoDB ObjectId (string) to auto-incrementing integer
  - Updated all database queries from MongoDB to SQL
  - Removed MongoDB connection configuration

### Added

- **SQLite Database Integration**
  - Implemented complete SQLite database layer with aiosqlite
  - Automatic schema creation on application startup
  - WAL mode for better concurrency
  - Connection pooling and transaction management
  - Database initialization and migration scripts

- **Data Migration Tool**
  - Created migration script (`backend/scripts/migrate_mongodb_to_sqlite.py`)
  - Supports migrating accounts, jobs, and tasks from MongoDB to SQLite
  - Includes progress reporting, data verification, and rollback safety
  - ObjectId to integer ID conversion
  - JSON field serialization for config/result data

- **Documentation**
  - Added `DEPLOYMENT.md` - Comprehensive deployment guide
  - Added `MIGRATION_SUMMARY.md` - Implementation summary
  - Updated `README.md` with SQLite information
  - Added pre-commit hooks configuration (`.pre-commit-config.yaml`)
  - Added Git hooks section to README

- **Development Tools**
  - Configured pre-commit hooks for code quality
  - Set up ruff for Python linting and formatting
  - Added commit-msg hook for Conventional Commits validation
  - Added pre-push hook for testing and type checking

### Changed

- **Database Layer** (`backend/app/core/database.py`)
  - Completely rewritten for SQLite
  - Async connection management with aiosqlite
  - WAL mode and foreign key support
  - Automatic schema initialization

- **Configuration** (`backend/app/core/config.py`)
  - Removed `MONGODB_URL` and `DATABASE_NAME`
  - Added `SQLITE_DB_PATH` configuration
  - Updated CORS origins to allow all sources in development

- **Schemas** (`backend/app/schemas/`)
  - Changed all ID fields from `str` to `int`
  - Updated examples to use integer IDs
  - Maintained datetime compatibility

- **Services** (`backend/app/services/`)
  - Completely rewritten for SQL queries
  - Removed all MongoDB ObjectId operations
  - Added parameterized queries for SQL injection prevention
  - Implemented JSON serialization for dict fields (tasks config/result)
  - Added timestamp management for created_at/updated_at

- **API Layer** (`backend/app/api/`)
  - Updated all endpoints to use aiosqlite.Connection
  - Changed ID parameters from str to int
  - Maintained API compatibility

- **Dependencies** (`backend/requirements.txt`, `backend/pyproject.toml`)
  - Removed: `motor==3.3.2`, `pymongo==4.6.0`
  - Added: `aiosqlite>=0.19.0`

### Fixed

- **CORS Configuration**
  - Fixed CORS origins to support frontend on port 5174
  - Changed to allow all origins in development mode

- **Code Quality**
  - Fixed all ruff linting errors (11 E501 line length issues, 1 N802 function name)
  - Formatted all Python code with ruff format
  - Removed unused imports and variables

### Technical Details

**Database Schema:**
- `accounts` table with auto-incrementing ID
- `jobs` table with auto-incrementing ID
- `tasks` table with auto-incrementing ID and JSON fields for config/result

**Migration Path:**
1. Fresh installations: Database created automatically on first run
2. Existing MongoDB data: Run migration script before starting application

**Backward Compatibility:**
- API endpoints unchanged (same URLs and request/response formats)
- ID serialization transparent (int in Python, number in JSON)
- All business logic preserved

### Performance

- Eliminated MongoDB server dependency
- Simplified deployment (single database file)
- Reduced resource usage
- Faster read operations for typical workloads
- WAL mode enables better concurrency

### Developer Experience

- Zero configuration database setup
- Simple file-based backups
- Better code quality with pre-commit hooks
- Automatic code formatting with ruff

### Migration Notes

If you have existing MongoDB data:
1. Backup your MongoDB database
2. Run: `python backend/scripts/migrate_mongodb_to_sqlite.py`
3. Start the application

### Documentation

- See `DEPLOYMENT.md` for detailed deployment guide
- See `MIGRATION_SUMMARY.md` for implementation details
- See `README.md` for quick start guide

---

## [1.0.0] - Initial Release

### Features
- BOSS直聘自动化招聘系统
- 职位搜索和自动投递
- 自动聊天功能
- 账户管理
- 任务调度

[1.1.0]: https://github.com/yourusername/RPA_BOSS-/compare/v1.0.0...v1.1.0
