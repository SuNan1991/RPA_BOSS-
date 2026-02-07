# Deployment Guide - MongoDB to SQLite Migration

## Overview

This document describes the migration from MongoDB to SQLite database.

## Migration Summary

### What Changed

- **Database**: MongoDB → SQLite
- **Python Driver**: Motor (async) → aiosqlite
- **ID Type**: MongoDB ObjectId (string) → Integer (int)
- **Dependencies**: Removed `motor` and `pymongo`, added `aiosqlite`

### What Stayed the Same

- All API endpoints remain unchanged
- All business logic preserved
- Data structures maintained (with ID type change)
- Application flow and features unchanged

## Pre-Migration Checklist

### 1. Backup MongoDB Data

```bash
# MongoDB backup
mongodump --db=boss_rpa --out=/path/to/backup

# Or export to JSON
mongoexport --db=boss_rpa --collection=accounts --out accounts.json
mongoexport --db=boss_rpa --collection=jobs --out jobs.json
mongoexport --db=boss_rpa --collection=tasks --out tasks.json
```

### 2. Verify MongoDB Access

```bash
# Check MongoDB is running
# Windows
net start MongoDB

# Linux/Mac
sudo systemctl status mongod

# Test connection
mongo mongodb://localhost:27017/boss_rpa
```

### 3. Stop Application

```bash
# Stop the running application
# Ctrl+C or kill the process
```

## Migration Steps

### Option A: Fresh Installation (No Data Migration)

If you don't need existing data:

1. **Update Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Remove Old MongoDB Dependencies** (if present)
   ```bash
   pip uninstall motor pymongo
   ```

3. **Start Application**
   ```bash
   python -m app.main
   ```

The application will automatically create the SQLite database and schema.

### Option B: Migrate Existing Data

If you have existing MongoDB data to migrate:

1. **Run Migration Script**
   ```bash
   cd backend
   python scripts/migrate_mongodb_to_sqlite.py
   ```

2. **Verify Migration**
   - Check the console output for record counts
   - Verify MongoDB count = SQLite count for each collection

3. **Start Application**
   ```bash
   python -m app.main
   ```

## Post-Migration Verification

### 1. Test API Endpoints

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test accounts list
curl http://localhost:8000/api/accounts/

# Test jobs list
curl http://localhost:8000/api/jobs/

# Test tasks list
curl http://localhost:8000/api/tasks/
```

### 2. Verify Data Integrity

- Check that all records are accessible
- Verify ID format changed (strings to integers)
- Test CRUD operations
- Check that timestamps are preserved

### 3. Monitor Logs

```bash
# Check for any errors
tail -f logs/app.log
```

## Rollback Plan

If issues occur:

1. **Stop Application**

2. **Restore MongoDB** (if needed)
   ```bash
   mongorestore --db=boss_rpa /path/to/backup/boss_rpa
   ```

3. **Rollback Code**
   ```bash
   git checkout <previous-commit>
   ```

4. **Reinstall Dependencies**
   ```bash
   pip install motor==3.3.2 pymongo==4.6.0
   pip uninstall aiosqlite
   ```

5. **Restart Application**

## Database Maintenance

### Backup

```bash
# Simple file copy
cp backend/data/boss_rpa.db backups/boss_rpa_$(date +%Y%m%d).db
```

### Query Database

```bash
# Using sqlite3 CLI
sqlite3 backend/data/boss_rpa.db

# View tables
.tables

# Query accounts
SELECT * FROM accounts LIMIT 10;

# Query jobs
SELECT * FROM jobs LIMIT 10;

# Query tasks
SELECT * FROM tasks LIMIT 10;
```

### Database File Location

- **Path**: `backend/data/boss_rpa.db`
- **Size**: Typically 1-10 MB for small datasets
- **Format**: SQLite 3 database file

## Performance Considerations

### SQLite Advantages

- ✅ Zero configuration
- ✅ Single file backup
- ✅ Low resource usage
- ✅ Fast for read operations
- ✅ Sufficient for single-instance applications

### SQLite Limitations

- ⚠️ Write operations are serialized
- ⚠️ Limited concurrency compared to client-server databases
- ⚠️ Not suitable for distributed systems

### When to Upgrade

Consider upgrading to PostgreSQL if:
- Multiple application instances need concurrent writes
- High write throughput (>100 writes/sec)
- Need advanced database features (replication, sharding, etc.)

## Troubleshooting

### Issue: Database Locked

**Error**: `sqlite3.OperationalError: database is locked`

**Solution**:
- Ensure only one application instance is running
- Check for background processes accessing the database
- Use WAL mode (enabled by default)

### Issue: Integer ID Not Found

**Error**: 404 when accessing resource by ID

**Solution**:
- IDs changed from string to integer
- Update API calls: use `1` instead of `"507f1f77bcf86cd799439011"`
- Clear frontend cache if needed

### Issue: Migration Script Fails

**Error**: Cannot connect to MongoDB

**Solution**:
1. Verify MongoDB is running
2. Check connection string in migration script
3. Ensure MongoDB authentication credentials are correct
4. Check firewall settings

### Issue: JSON Fields Not Loading

**Error**: Tasks with config/result return empty dicts

**Solution**:
- This is expected if JSON fields are empty
- Check database: `SELECT id, config FROM tasks LIMIT 5;`
- Verify JSON serialization in task_service.py

## Configuration Changes

### Removed Configuration

```bash
# Remove from .env or config
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=boss_rpa
```

### Added Configuration

```bash
# Add to .env or config
SQLITE_DB_PATH=data/boss_rpa.db
```

## API Changes

### Internal Changes

- **Service Layer**: Changed from MongoDB queries to SQL queries
- **Dependency Injection**: Changed from `AsyncIOMotorDatabase` to `aiosqlite.Connection`
- **ID Type**: Changed from `str` to `int` in service layer

### No Breaking Changes

- All API endpoints remain the same
- Request/response formats unchanged (IDs serialized as JSON numbers)
- No changes required for API consumers

## Monitoring

### Database Size Monitoring

```bash
# Check database file size
ls -lh backend/data/boss_rpa.db
```

### Query Performance

```bash
# Enable SQLite query logging
# In database.py, add:
# await self.conn.execute("PRAGMA optimize")
```

## Migration Timeline

### Phase 1: Development (Completed)
- ✅ Rewrite database layer
- ✅ Update service layer
- ✅ Update API layer
- ✅ Create migration script

### Phase 2: Testing (Recommended)
- Test all API endpoints
- Verify data integrity
- Load testing
- Performance benchmarking

### Phase 3: Production (When Ready)
- Backup MongoDB data
- Run migration script
- Verify migration
- Deploy application
- Monitor for 24-48 hours
- Keep MongoDB backup for 1 week

## Support

For issues or questions:
1. Check application logs: `logs/app.log`
2. Review this migration guide
3. Check SQLite documentation: https://www.sqlite.org/docs.html
4. Check aiosqlite documentation: https://aiosqlite.omnilib.dev

## Success Criteria

Migration is successful when:
- ✅ All existing data migrated without loss
- ✅ All API endpoints working correctly
- ✅ No errors in application logs
- ✅ Performance acceptable
- ✅ ID format change transparent to users

---

**Last Updated**: 2026-02-06
**Migration Version**: 1.0.0
