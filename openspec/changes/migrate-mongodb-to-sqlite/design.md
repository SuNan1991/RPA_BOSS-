# Design: MongoDB to SQLite Migration

## Context

The application currently uses MongoDB as its primary database with Motor (async driver). The database consists of three collections: `accounts`, `jobs`, and `tasks`. All database operations are performed asynchronously through a service layer that abstracts MongoDB queries. The application is a FastAPI-based RPA platform with RESTful APIs that depend on these database services.

**Current Architecture:**
- MongoDB connection via Motor (`mongodb://localhost:27017/boss_rpa`)
- Service layer with async CRUD operations
- Pydantic schemas for data validation
- MongoDB ObjectId as primary identifier (exposed as strings in APIs)

**Constraints:**
- Must preserve all existing API contracts
- Must maintain async operation model
- Must preserve all existing business logic
- Must provide data migration path from MongoDB to SQLite
- Must handle existing deployments with MongoDB data

## Goals / Non-Goals

**Goals:**
- Replace MongoDB with SQLite as the primary database
- Eliminate MongoDB server dependency for simplified deployment
- Maintain all existing API functionality and contracts
- Provide seamless data migration from MongoDB to SQLite
- Preserve async operation model using aiosqlite
- Ensure zero data loss during migration
- Remove all MongoDB-related code and dependencies

**Non-Goals:**
- Changing API contracts or behavior
- Adding new features or capabilities beyond the migration
- Supporting dual database operation (MongoDB + SQLite simultaneously)
- Performance optimization (though SQLite may provide performance benefits)
- Schema redesign beyond what's necessary for SQLite compatibility

## Decisions

### 1. Use aiosqlite for Async Operations

**Decision:** Use aiosqlite library instead of building custom async wrappers around sqlite3.

**Rationale:**
- Provides drop-in async compatibility with existing async codebase
- Maintains async/await pattern throughout the application
- Well-maintained library with active development
- Compatible with Python's asyncio ecosystem

**Alternatives Considered:**
- **synchronous sqlite3**: Would require rewriting entire async stack
- **SQLAlchemy core**: Overkill for simple queries, adds complexity
- **SQLAlchemy ORM**: Too heavy for this use case, steep learning curve

### 2. Auto-Incrementing Integer IDs

**Decision:** Replace MongoDB ObjectId with auto-incrementing integer primary keys.

**Rationale:**
- Simpler and more natural for relational databases
- Easier to debug and reference
- Smaller storage footprint compared to ObjectId strings
- Compatible with existing API expectations (IDs as strings in JSON)
- Maps cleanly to existing Pydantic models (str → int in schema, string in JSON)

**Alternatives Considered:**
- **UUIDs**: Unnecessary complexity, larger storage, no clear benefit
- **Composite keys**: Overcomplicates foreign key relationships
- **Keep ObjectId strings**: Not idiomatic for SQLite, loses performance benefits

### 3. Direct SQL Queries in Service Layer

**Decision:** Write raw SQL queries in service layer instead of using ORM.

**Rationale:**
- Existing service layer already has query logic
- Simpler migration path (translate MongoDB queries to SQL)
- More explicit and easier to debug
- No additional ORM dependency to learn
- Fine-grained control over query optimization

**Alternatives Considered:**
- **SQLAlchemy ORM**: Adds abstraction layer, migration complexity
- **Peewee**: Lighter than SQLAlchemy but still requires learning new API
- **SQLAlchemy Core**: Good middle ground but more setup than direct SQL

### 4. Single Database File with Connection Pool

**Decision:** Use single SQLite file with connection pooling via aiosqlite.

**Rationale:**
- Simplifies deployment (single file backup/migration)
- SQLite supports concurrent reads well
- Write operations are serialized by SQLite (acceptable for this workload)
- WAL (Write-Ahead Logging) mode enables better concurrency
- Connection reuse reduces overhead

**Alternatives Considered:**
- **Multiple database files**: Unnecessary complexity, no clear benefit
- **In-memory database**: Loses persistence, not suitable for production
- **Separate read/write connections**: Overkill for current load patterns

### 5. WAL Mode for Concurrency

**Decision:** Enable SQLite WAL (Write-Ahead Logging) mode.

**Rationale:**
- Allows simultaneous readers and writers
- Better concurrency than default journal mode
- Reduces contention for RPA workload (frequent writes)
- Standard practice for production SQLite databases

**Configuration:**
```sql
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
```

### 6. Schema Design

**Decision:** Normalized schema with foreign key relationships.

**Rationale:**
- Maintains data integrity
- Maps naturally to existing document relationships
- Enables proper indexing and constraints
- Supports future query optimizations

**Table Structure:**

```sql
-- accounts table
CREATE TABLE accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT NOT NULL UNIQUE,
    username TEXT,
    is_active BOOLEAN DEFAULT 1,
    cookie_status TEXT DEFAULT 'none',
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- jobs table
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_name TEXT NOT NULL,
    company_name TEXT NOT NULL,
    salary TEXT,
    city TEXT,
    area TEXT,
    experience TEXT,
    education TEXT,
    company_size TEXT,
    industry TEXT,
    job_url TEXT NOT NULL,
    boss_title TEXT,
    status TEXT DEFAULT 'pending',
    is_applied BOOLEAN DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- tasks table
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    task_type TEXT NOT NULL,
    config TEXT,  -- JSON stored as TEXT
    status TEXT DEFAULT 'pending',
    result TEXT,  -- JSON stored as TEXT
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 7. Data Migration Strategy

**Decision:** One-time migration script with transaction rollback support.

**Rationale:**
- Atomic migration prevents partial data loss
- Transaction allows rollback on failure
- Can be run multiple times idempotently
- Provides clear success/failure feedback

**Migration Steps:**
1. Connect to MongoDB and SQLite
2. Start SQLite transaction
3. Migrate accounts collection → accounts table
4. Migrate jobs collection → jobs table
5. Migrate tasks collection → tasks table
6. Verify data integrity
7. Commit transaction or rollback on error

**Implementation:**
- Standalone Python script (`scripts/migrate_mongodb_to_sqlite.py`)
- Uses both Motor and aiosqlite simultaneously
- Progress reporting during migration
- Transaction safety with error handling

### 8. Database Initialization

**Decision:** Automatic schema creation on application startup if database file doesn't exist.

**Rationale:**
- Zero-configuration deployment
- Fresh installations work immediately
- Schema version tracking for future migrations
- Idempotent (safe to run multiple times)

**Implementation:**
```python
async def init_database():
    if not exists(database_file):
        await create_schema()
        await apply_migrations()
```

### 9. Backward Compatibility

**Decision:** Maintain API compatibility by handling IDs as strings in JSON.

**Rationale:**
- Existing API consumers expect string IDs
- JSON serialization handles int → str conversion naturally
- No breaking changes for API users
- Internal use of integers is transparent

**Implementation:**
- Pydantic schemas define IDs as `int` internally
- FastAPI automatically serializes integers in JSON responses
- API requests accept string IDs, converted to int in service layer

## Risks / Trade-offs

### Risk 1: Data Loss During Migration

**Risk:** Migration script fails or produces inconsistent data.

**Mitigation:**
- Use SQLite transactions for atomic migration
- Validate data integrity after migration
- Keep MongoDB backup during migration period
- Provide rollback functionality
- Test migration script thoroughly on staging data

### Risk 2: Concurrency Limitations

**Risk:** SQLite write locks may cause contention under high load.

**Mitigation:**
- Enable WAL mode for better concurrency
- RPA workload is primarily read-heavy (acceptable)
- Monitor performance in production
- Future: Add connection pooling if needed
- Future: Migrate to PostgreSQL if scalability becomes issue

### Risk 3: ID Type Changes Break References

**Risk:** Integer IDs may break systems expecting MongoDB ObjectId strings.

**Mitigation:**
- API layer handles serialization (int → str in JSON)
- Verify all external integrations accept string IDs
- Test with real API clients
- Document ID format for API consumers

### Risk 4: JSON Field Handling

**Risk:** Tasks.config and tasks.result stored as JSON need proper handling.

**Mitigation:**
- Store JSON as TEXT in SQLite
- Serialize/deserialize in service layer using `json.loads()` and `json.dumps()`
- Add helper functions for JSON field operations
- Validate JSON structure on write

### Risk 5: Query Translation Errors

**Risk:** MongoDB queries may not translate perfectly to SQL.

**Mitigation:**
- Thorough testing of all service methods
- Compare query results between MongoDB and SQLite versions
- Add integration tests for all CRUD operations
- Manual code review of query translations

## Migration Plan

### Phase 1: Development (Local Environment)

1. Set up SQLite with aiosqlite
2. Implement database connection layer
3. Create schema initialization scripts
4. Rewrite service layer for SQL queries
5. Update Pydantic schemas (ObjectId → int)
6. Write migration script
7. Test all API endpoints with SQLite
8. Verify data migration script

### Phase 2: Testing (Staging Environment)

1. Deploy to staging with SQLite
2. Run migration script on staging MongoDB data
3. Execute full integration test suite
4. Perform load testing
5. Verify all functionality matches MongoDB version
6. Fix any discovered issues

### Phase 3: Production Migration (Downtime Required)

**Pre-Migration:**
1. Backup production MongoDB database
2. Notify users of scheduled maintenance window
3. Deploy new SQLite version to production (without traffic)
4. Verify SQLite database file creation

**Migration:**
1. Stop application (no traffic)
2. Run migration script on production MongoDB data
3. Verify migration success (row counts, sample queries)
4. Start application with SQLite
5. Smoke test critical API endpoints
6. Monitor for errors

**Post-Migration:**
1. Monitor application for 24-48 hours
2. Keep MongoDB backup for 1 week
3. Remove MongoDB dependencies from deployment
4. Document migration completion

**Rollback Strategy:**
- If critical issues discovered, revert to previous version with MongoDB
- Restore from MongoDB backup
- Requires redeploying old version
- Max downtime: 30 minutes (migration + verification)

## Open Questions

1. **Timestamp Precision**: MongoDB stores timestamps with millisecond precision. Should SQLite match this exactly or is second precision sufficient?
   - **Recommendation**: Use millisecond precision (store as ISO string or epoch milliseconds)

2. **JSON Field Indexing**: Should we create indexes on JSON field contents (e.g., tasks.config)?
   - **Recommendation**: No, defer until specific query patterns emerge. SQLite JSON1 extension can be added later.

3. **Database File Location**: Where should the SQLite file be stored relative to the application?
   - **Recommendation**: `backend/data/boss_rpa.db` (gitignored)

4. **Schema Migrations**: How should future schema changes be handled?
   - **Recommendation**: Implement simple migration tracking table (version number + applied migrations)

5. **Connection Pool Size**: What's the optimal connection pool size for aiosqlite?
   - **Recommendation**: Start with 5 connections, adjust based on monitoring
