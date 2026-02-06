# Implementation Tasks: MongoDB to SQLite Migration

## 1. Setup and Dependencies

- [x] 1.1 Add aiosqlite dependency to `backend/requirements.txt`
- [x] 1.2 Remove motor and pymongo dependencies from `backend/requirements.txt`
- [x] 1.3 Install new dependencies (`pip install -r requirements.txt`)
- [x] 1.4 Create `backend/data/` directory for SQLite database file
- [x] 1.5 Add `backend/data/` to `.gitignore`

## 2. Database Connection Layer

- [x] 2.1 Rewrite `backend/app/core/database.py` to use aiosqlite instead of Motor
- [x] 2.2 Implement `Database` class with async context manager support
- [x] 2.3 Implement connection pool management
- [x] 2.4 Add `get_database()` dependency injection function
- [x] 2.5 Configure WAL mode and connection pragmas in initialization
- [x] 2.6 Add database configuration to `backend/app/core/config.py`

## 3. Schema Creation

- [x] 3.1 Create `backend/app/core/schema.sql` with table definitions
- [x] 3.2 Implement `create_schema()` function to execute SQL schema
- [x] 3.3 Add accounts table with auto-incrementing ID and indexes
- [x] 3.4 Add jobs table with auto-incrementing ID and indexes
- [x] 3.5 Add tasks table with auto-incrementing ID and indexes
- [x] 3.6 Add `init_database()` function to check and create schema on startup
- [x] 3.7 Integrate schema initialization into application startup

## 4. Pydantic Schema Updates

- [x] 4.1 Update `backend/app/schemas/account.py`: Change `id` field from `str` to `int`
- [x] 4.2 Update `backend/app/schemas/job.py`: Change `id` field from `str` to `int`
- [x] 4.3 Update `backend/app/schemas/task.py`: Change `id` field from `str` to `int`
- [x] 4.4 Verify all datetime fields use compatible formats
- [x] 4.5 Update config and result fields to handle JSON serialization properly

## 5. Account Service Migration

- [x] 5.1 Update `backend/app/services/account_service.py` imports (remove ObjectId, add aiosqlite)
- [x] 5.2 Rewrite `create_account()` to use INSERT SQL query
- [x] 5.3 Rewrite `get_account_by_id()` to use SELECT query with integer ID
- [x] 5.4 Rewrite `get_account_by_phone()` to use SELECT query with parameter
- [x] 5.5 Rewrite `get_accounts()` to use SELECT with optional filters
- [x] 5.6 Rewrite `update_account()` to use UPDATE query
- [x] 5.7 Rewrite `update_cookie_status()` to use UPDATE query
- [x] 5.8 Rewrite `delete_account()` to use DELETE query
- [x] 5.9 Remove all ObjectId conversion logic
- [x] 5.10 Add timestamp management (created_at, updated_at)

## 6. Job Service Migration

- [x] 6.1 Update `backend/app/services/job_service.py` imports (remove ObjectId, add aiosqlite)
- [x] 6.2 Rewrite `create_job()` to use INSERT SQL query
- [x] 6.3 Rewrite `get_job_by_id()` to use SELECT query with integer ID
- [x] 6.4 Rewrite `get_jobs()` to use SELECT with optional filters
- [x] 6.5 Rewrite `batch_create_jobs()` to use executemany INSERT
- [x] 6.6 Rewrite `update_job()` to use UPDATE query
- [x] 6.7 Rewrite `delete_job()` to use DELETE query
- [x] 6.8 Remove all ObjectId conversion logic
- [x] 6.9 Add timestamp management (created_at, updated_at)

## 7. Task Service Migration

- [x] 7.1 Update `backend/app/services/task_service.py` imports (remove ObjectId, add aiosqlite)
- [x] 7.2 Rewrite `create_task()` to use INSERT with JSON serialization for config
- [x] 7.3 Rewrite `get_task_by_id()` to use SELECT with JSON deserialization
- [x] 7.4 Rewrite `get_tasks()` to use SELECT with JSON handling
- [x] 7.5 Rewrite `update_task()` to use UPDATE with JSON serialization
- [x] 7.6 Rewrite `update_task_status()` to use UPDATE query
- [x] 7.7 Rewrite `delete_task()` to use DELETE query
- [x] 7.8 Remove all ObjectId conversion logic
- [x] 7.9 Add JSON serialization/deserialization helpers
- [x] 7.10 Add timestamp management (created_at, updated_at)

## 8. Data Migration Script

- [x] 8.1 Create `backend/scripts/migrate_mongodb_to_sqlite.py`
- [x] 8.2 Implement MongoDB connection using Motor
- [x] 8.3 Implement SQLite connection using aiosqlite
- [x] 8.4 Implement accounts collection migration
- [x] 8.5 Implement jobs collection migration
- [x] 8.6 Implement tasks collection migration (with JSON handling)
- [x] 8.7 Implement ObjectId to integer ID conversion logic
- [x] 8.8 Implement data type conversion (datetime, boolean, dict)
- [x] 8.9 Add transaction management with rollback on error
- [x] 8.10 Add progress reporting during migration
- [x] 8.11 Add data integrity verification (record counts, sampling)
- [x] 8.12 Add backup recommendation and user confirmation
- [x] 8.13 Add error handling with clear messages
- [x] 8.14 Add configuration loading for MongoDB and SQLite connections
- [x] 8.15 Test migration script on sample data

## 9. Testing

- [ ] 9.1 Test database connection and initialization
- [ ] 9.2 Test all account CRUD operations
- [ ] 9.3 Test all job CRUD operations
- [ ] 9.4 Test all task CRUD operations
- [ ] 9.5 Test JSON field serialization/deserialization
- [ ] 9.6 Test parameterized queries prevent SQL injection
- [ ] 9.7 Test API endpoints with SQLite backend
- [ ] 9.8 Test pagination and filtering queries
- [ ] 9.9 Test transaction rollback on errors
- [ ] 9.10 Run migration script on test MongoDB data
- [ ] 9.11 Verify migrated data integrity
- [ ] 9.12 Test idempotent migration (re-run safely)

## 10. API Integration Testing

- [ ] 10.1 Test all account API endpoints (`/api/accounts/*`)
- [ ] 10.2 Test all job API endpoints (`/api/jobs/*`)
- [ ] 10.3 Test all task API endpoints (`/api/tasks/*`)
- [ ] 10.4 Verify API responses maintain same structure
- [ ] 10.5 Verify ID serialization (int to string in JSON)
- [ ] 10.6 Test error handling and status codes

## 11. Documentation

- [x] 11.1 Update `README.md` with SQLite setup instructions
- [x] 11.2 Remove MongoDB installation instructions
- [x] 11.3 Add data migration guide
- [x] 11.4 Update deployment documentation
- [x] 11.5 Document database file location and backup procedure
- [x] 11.6 Document schema changes (ObjectId → integer IDs)

## 12. Cleanup

- [x] 12.1 Remove MongoDB connection code from `database.py`
- [x] 12.2 Remove MongoDB-specific comments and documentation
- [x] 12.3 Verify no remaining MongoDB imports in codebase
- [ ] 12.4 Clean up any unused variables or functions
- [ ] 12.5 Run linter and fix any issues
- [x] 12.6 Final code review and cleanup

## 13. Production Deployment

- [ ] 13.1 Create production MongoDB backup
- [ ] 13.2 Schedule maintenance window
- [ ] 13.3 Deploy new SQLite version to production
- [ ] 13.4 Run migration script on production data
- [ ] 13.5 Verify migration success
- [ ] 13.6 Monitor application for 24-48 hours
- [ ] 13.7 Remove MongoDB server (after verification period)
