# Data Migration Capability

## ADDED Requirements

### Requirement: MongoDB to SQLite Migration
The system SHALL provide a standalone migration script to transfer data from MongoDB to SQLite.

#### Scenario: Run complete migration
- **WHEN** migration script is executed
- **THEN** system SHALL connect to MongoDB database
- **AND** system SHALL connect to SQLite database
- **AND** system SHALL begin SQLite transaction
- **AND** system SHALL migrate all accounts from MongoDB to SQLite
- **AND** system SHALL migrate all jobs from MongoDB to SQLite
- **AND** system SHALL migrate all tasks from MongoDB to SQLite
- **AND** system SHALL verify data integrity
- **AND** system SHALL commit transaction
- **AND** system SHALL report migration statistics

#### Scenario: Migrate accounts collection
- **WHEN** migrating accounts
- **THEN** system SHALL read all documents from MongoDB accounts collection
- **AND** system SHALL convert MongoDB ObjectId to integer ID
- **AND** system SHALL map document fields to table columns
- **AND** system SHALL convert MongoDB timestamps to SQLite TIMESTAMP format
- **AND** system SHALL preserve phone uniqueness constraint
- **AND** system SHALL INSERT all accounts into SQLite accounts table

#### Scenario: Migrate jobs collection
- **WHEN** migrating jobs
- **THEN** system SHALL read all documents from MongoDB jobs collection
- **AND** system SHALL convert MongoDB ObjectId to integer ID
- **AND** system SHALL map document fields to table columns
- **AND** system SHALL convert MongoDB timestamps to SQLite TIMESTAMP format
- **AND** system SHALL handle missing optional fields (set to NULL)
- **AND** system shall INSERT all jobs into SQLite jobs table

#### Scenario: Migrate tasks collection
- **WHEN** migrating tasks
- **THEN** system SHALL read all documents from MongoDB tasks collection
- **AND** system SHALL convert MongoDB ObjectId to integer ID
- **AND** system SHALL map document fields to table columns
- **AND** system SHALL serialize config dict to JSON TEXT
- **AND** system SHALL serialize result dict to JSON TEXT if present
- **AND** system SHALL convert MongoDB timestamps to SQLite TIMESTAMP format
- **AND** system shall INSERT all tasks into SQLite tasks table

### Requirement: Data Type Conversion
The system SHALL correctly convert MongoDB data types to SQLite-compatible formats.

#### Scenario: Convert ObjectId to integer
- **WHEN** converting MongoDB ObjectId
- **THEN** system SHALL assign sequential integer ID starting from 1
- **AND** system SHALL maintain ID uniqueness within each table
- **AND** system SHALL preserve insertion order (first document = ID 1)

#### Scenario: Convert datetime
- **WHEN** converting MongoDB datetime
- **THEN** system SHALL convert to ISO 8601 string format
- **AND** system SHALL preserve millisecond precision
- **AND** system SHALL handle NULL datetime values

#### Scenario: Convert boolean
- **WHEN** converting MongoDB boolean
- **THEN** system SHALL map True to 1
- **AND** system SHALL map False to 0
- **AND** system SHALL store as INTEGER in SQLite

#### Scenario: Convert dict to JSON
- **WHEN** converting MongoDB dict (config, result)
- **THEN** system SHALL serialize to JSON string
- **AND** system SHALL preserve nested structure
- **AND** system SHALL handle empty dict (serialize to {})

#### Scenario: Convert string
- **WHEN** converting MongoDB string
- **THEN** system SHALL preserve string value
- **AND** system SHALL handle empty string
- **AND** system SHALL handle NULL (missing field)

### Requirement: Transaction Safety
The system SHALL use SQLite transactions to ensure atomic migration.

#### Scenario: Successful migration commits
- **WHEN** all data migrations complete without errors
- **THEN** system SHALL commit SQLite transaction
- **AND** system SHALL persist all changes
- **AND** system SHALL report success

#### Scenario: Failed migration rolls back
- **WHEN** any error occurs during migration
- **THEN** system SHALL rollback SQLite transaction
- **AND** system SHALL undo all partial changes
- **AND** system SHALL report error with details
- **AND** system SHALL leave SQLite database in clean state

### Requirement: Data Integrity Verification
The system SHALL verify migrated data integrity.

#### Scenario: Verify record counts
- **WHEN** migration completes
- **THEN** system SHALL count records in MongoDB collections
- **AND** system SHALL count records in SQLite tables
- **AND** system SHALL verify counts match
- **AND** system SHALL report any discrepancies

#### Scenario: Verify data samples
- **WHEN** migration completes
- **THEN** system SHALL sample 10 random records from each table
- **AND** system SHALL verify field presence and types
- **AND** system SHALL report any corruption

### Requirement: Idempotent Migration
The system SHALL support running migration multiple times safely.

#### Scenario: Re-run migration
- **WHEN** migration is run on already-migrated SQLite database
- **THEN** system SHALL detect existing data
- **AND** system SHALL warn user about potential duplicate IDs
- **AND** system SHALL offer to clear SQLite tables before migration
- **OR** system SHALL abort if user declines

### Requirement: Progress Reporting
The system SHALL report migration progress during execution.

#### Scenario: Report account migration progress
- **WHEN** migrating accounts
- **THEN** system SHALL report total accounts to migrate
- **AND** system SHALL update progress every 100 records
- **AND** system SHALL display completion percentage

#### Scenario: Report job migration progress
- **WHEN** migrating jobs
- **THEN** system SHALL report total jobs to migrate
- **AND** system SHALL update progress every 100 records
- **AND** system SHALL display completion percentage

#### Scenario: Report task migration progress
- **WHEN** migrating tasks
- **THEN** system SHALL report total tasks to migrate
- **AND** system SHALL update progress every 100 records
- **AND** system SHALL display completion percentage

#### Scenario: Report final statistics
- **WHEN** migration completes
- **THEN** system SHALL report total accounts migrated
- **AND** system SHALL report total jobs migrated
- **AND** system SHALL report total tasks migrated
- **AND** system SHALL report total migration duration
- **AND** system SHALL report any warnings or errors

### Requirement: Configuration
The system SHALL support configurable MongoDB and SQLite connection details.

#### Scenario: Load migration configuration
- **WHEN** migration script starts
- **THEN** system SHALL read MongoDB connection URL from config
- **AND** system SHALL read MongoDB database name from config
- **AND** system SHALL read SQLite database file path from config
- **AND** system SHALL use defaults if not provided

### Requirement: Error Handling
The system SHALL provide clear error messages and recovery suggestions.

#### Scenario: Handle MongoDB connection error
- **WHEN** MongoDB connection fails
- **THEN** system SHALL report connection error
- **AND** error SHALL include MongoDB URL
- **AND** error SHALL suggest checking MongoDB server is running
- **AND** system SHALL exit with error code

#### Scenario: Handle SQLite creation error
- **WHEN** SQLite database creation fails
- **THEN** system SHALL report file system error
- **AND** error SHALL include file path
- **AND** error SHALL suggest checking directory permissions
- **AND** system SHALL exit with error code

#### Scenario: Handle data conversion error
- **WHEN** document conversion fails
- **THEN** system SHALL report conversion error
- **AND** error SHALL include document ID and field name
- **AND** error SHALL include original value
- **AND** system SHALL rollback transaction
- **AND** system SHALL exit with error code

### Requirement: Backup Recommendation
The system SHALL recommend backing up MongoDB before migration.

#### Scenario: Warn about backup
- **WHEN** migration script starts
- **THEN** system SHALL display backup warning
- **AND** system SHALL recommend creating MongoDB dump
- **AND** system SHALL offer command to create backup
- **AND** system SHALL require user confirmation to proceed
