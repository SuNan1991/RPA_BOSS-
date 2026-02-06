# Proposal: Migrate from MongoDB to SQLite

## Why

MongoDB introduces unnecessary complexity and operational overhead for this RPA application. SQLite provides a simpler, self-contained solution that eliminates the need for a separate database server, reduces deployment complexity, and lowers the barrier to entry for users running the application locally.

## What Changes

- **BREAKING**: Replace MongoDB (Motor) with SQLite (aiosqlite) as the primary database
- **BREAKING**: Remove all MongoDB-related dependencies (motor, pymongo)
- **BREAKING**: Replace MongoDB document collections with SQLite relational tables
- **BREAKING**: Convert MongoDB ObjectId identifiers to auto-incrementing integer IDs
- **BREAKING**: Remove MongoDB-specific query patterns and replace with SQL queries
- Update database connection layer from Motor to aiosqlite
- Migrate service layer to use SQL queries instead of MongoDB operations
- Remove all MongoDB configuration and connection code
- Add SQLite database initialization and schema migration scripts
- Preserve all existing API contracts and business logic

## Capabilities

### New Capabilities
- `sqlite-database`: Core SQLite database connection, initialization, and lifecycle management
- `sql-data-access`: SQL-based CRUD operations for accounts, jobs, and tasks
- `data-migration`: One-time migration script to transfer existing MongoDB data to SQLite

### Modified Capabilities
- None: The migration preserves all API behavior and business logic requirements

## Impact

**Affected Code:**
- `backend/app/core/database.py`: Complete rewrite for SQLite connection management
- `backend/app/services/account.py`: Update queries from MongoDB to SQL
- `backend/app/services/job.py`: Update queries from MongoDB to SQL
- `backend/app/services/task.py`: Update queries from MongoDB to SQL
- `backend/app/schemas/*.py`: Update ID fields from ObjectId to integers
- `backend/requirements.txt`: Remove motor/pymongo, add aiosqlite

**Dependencies:**
- Remove: `motor==3.3.2`, `pymongo==4.6.0`
- Add: `aiosqlite>=0.19.0`

**Data Migration:**
- Existing MongoDB data must be migrated to SQLite before deployment
- MongoDB collections (`accounts`, `jobs`, `tasks`) → SQLite tables
- ObjectId values → auto-incrementing integer IDs
- Document structure → relational schema with proper foreign keys

**API Impact:**
- No API contract changes (same endpoints, same request/response formats)
- Internal ID representation changes from string (ObjectId) to integer
- All existing API consumers remain compatible

**Deployment Impact:**
- Eliminates need for MongoDB server installation/operation
- Database stored as single file in application directory
- Simplifies backup and migration (file copy vs. database dump)
- Reduces system requirements and deployment complexity
