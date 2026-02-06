# SQL Data Access Capability

## ADDED Requirements

### Requirement: Account CRUD Operations
The system SHALL provide CRUD operations for accounts using SQL queries.

#### Scenario: Create account
- **WHEN** service creates a new account with phone number
- **THEN** system SHALL INSERT into accounts table
- **AND** system SHALL generate auto-incrementing integer ID
- **AND** system SHALL set created_at and updated_at timestamps
- **AND** system SHALL return created account with ID

#### Scenario: Get account by ID
- **WHEN** service requests account by integer ID
- **THEN** system SHALL SELECT from accounts table WHERE id = ?
- **AND** system SHALL return account record
- **OR** system SHALL return None if not found

#### Scenario: Get account by phone
- **WHEN** service requests account by phone number
- **THEN** system SHALL SELECT from accounts table WHERE phone = ?
- **AND** system SHALL return account record
- **OR** system SHALL return None if not found

#### Scenario: List accounts
- **WHEN** service requests list of accounts
- **THEN** system SHALL SELECT * from accounts table
- **AND** system SHALL support optional filters (is_active, cookie_status)
- **AND** system SHALL return list of account records
- **AND** system SHALL support pagination (skip, limit)

#### Scenario: Update account
- **WHEN** service updates account by ID
- **THEN** system SHALL UPDATE accounts table
- **AND** system SHALL set updated_at to current timestamp
- **AND** system SHALL apply provided field changes
- **AND** system SHALL return updated account

#### Scenario: Update account cookie status
- **WHEN** service updates account cookie_status
- **THEN** system SHALL UPDATE accounts table SET cookie_status = ?, updated_at = NOW()
- **AND** system SHALL return updated account

#### Scenario: Delete account
- **WHEN** service deletes account by ID
- **THEN** system SHALL DELETE from accounts table WHERE id = ?
- **AND** system SHALL return True if deleted
- **AND** system SHALL return False if not found

### Requirement: Job CRUD Operations
The system SHALL provide CRUD operations for jobs using SQL queries.

#### Scenario: Create job
- **WHEN** service creates a new job
- **THEN** system SHALL INSERT into jobs table
- **AND** system SHALL generate auto-incrementing integer ID
- **AND** system SHALL set created_at and updated_at timestamps
- **AND** system SHALL return created job with ID

#### Scenario: Get job by ID
- **WHEN** service requests job by integer ID
- **THEN** system SHALL SELECT from jobs table WHERE id = ?
- **AND** system SHALL return job record
- **OR** system SHALL return None if not found

#### Scenario: List jobs
- **WHEN** service requests list of jobs
- **THEN** system SHALL SELECT * from jobs table
- **AND** system SHALL support optional filters (status, city, company_name)
- **AND** system SHALL support sorting by created_at, updated_at
- **AND** system SHALL return list of job records
- **AND** system SHALL support pagination (skip, limit)

#### Scenario: Batch create jobs
- **WHEN** service creates multiple jobs
- **THEN** system SHALL executemany INSERT into jobs table
- **AND** system SHALL use transaction for atomicity
- **AND** system SHALL return list of created jobs with IDs

#### Scenario: Update job
- **WHEN** service updates job by ID
- **THEN** system SHALL UPDATE jobs table
- **AND** system SHALL set updated_at to current timestamp
- **AND** system SHALL apply provided field changes
- **AND** system SHALL return updated job

#### Scenario: Delete job
- **WHEN** service deletes job by ID
- **THEN** system SHALL DELETE from jobs table WHERE id = ?
- **AND** system SHALL return True if deleted
- **AND** system SHALL return False if not found

### Requirement: Task CRUD Operations
The system SHALL provide CRUD operations for tasks using SQL queries with JSON field handling.

#### Scenario: Create task
- **WHEN** service creates a new task
- **THEN** system SHALL INSERT into tasks table
- **AND** system SHALL serialize config dict to JSON TEXT
- **AND** system SHALL generate auto-incrementing integer ID
- **AND** system SHALL set created_at and updated_at timestamps
- **AND** system SHALL return created task with ID

#### Scenario: Get task by ID
- **WHEN** service requests task by integer ID
- **THEN** system SHALL SELECT from tasks table WHERE id = ?
- **AND** system SHALL deserialize config JSON TEXT to dict
- **AND** system SHALL deserialize result JSON TEXT to dict if present
- **AND** system SHALL return task record
- **OR** system SHALL return None if not found

#### Scenario: List tasks
- **WHEN** service requests list of tasks
- **THEN** system SHALL SELECT * from tasks table
- **AND** system SHALL support optional filters (status, task_type)
- **AND** system SHALL deserialize JSON fields to dicts
- **AND** system SHALL return list of task records
- **AND** system SHALL support pagination (skip, limit)

#### Scenario: Update task
- **WHEN** service updates task by ID
- **THEN** system SHALL UPDATE tasks table
- **AND** system SHALL serialize config dict to JSON TEXT if provided
- **AND** system SHALL set updated_at to current timestamp
- **AND** system SHALL apply provided field changes
- **AND** system SHALL return updated task

#### Scenario: Update task status
- **WHEN** service updates task status
- **THEN** system SHALL UPDATE tasks table SET status = ?, updated_at = NOW()
- **AND** system SHALL return updated task

#### Scenario: Update task result
- **WHEN** service updates task with result
- **THEN** system SHALL UPDATE tasks table
- **AND** system SHALL serialize result dict to JSON TEXT
- **AND** system SHALL set updated_at to current timestamp
- **AND** system SHALL return updated task

#### Scenario: Delete task
- **WHEN** service deletes task by ID
- **THEN** system SHALL DELETE from tasks table WHERE id = ?
- **AND** system SHALL return True if deleted
- **AND** system SHALL return False if not found

### Requirement: Query Parameter Safety
The system SHALL use parameterized queries to prevent SQL injection.

#### Scenario: Safe query parameters
- **WHEN** executing SQL with user-provided values
- **THEN** system SHALL use ? placeholders in SQL
- **AND** system SHALL pass parameters as separate arguments
- **AND** system SHALL NOT interpolate values into SQL string

### Requirement: ID Type Conversion
The system SHALL handle integer IDs internally and string IDs in API layer.

#### Scenario: Internal ID handling
- **WHEN** service layer performs database operations
- **THEN** system SHALL use integer IDs for database queries
- **AND** system SHALL store integer IDs in database

#### Scenario: API ID serialization
- **WHEN** API layer returns data to client
- **THEN** system SHALL serialize integer IDs to JSON-compatible format
- **AND** client SHALL receive IDs as numbers or strings per JSON spec

### Requirement: Timestamp Management
The system SHALL automatically manage created_at and updated_at timestamps.

#### Scenario: Set created timestamp
- **WHEN** creating new record
- **THEN** system SHALL set created_at to current timestamp
- **AND** system SHALL set updated_at to current timestamp

#### Scenario: Update timestamp
- **WHEN** updating existing record
- **THEN** system SHALL update updated_at to current timestamp
- **AND** system SHALL NOT modify created_at

### Requirement: JSON Field Handling
The system SHALL serialize and deserialize JSON fields for TEXT columns.

#### Scenario: Serialize JSON on insert
- **WHEN** saving dict to config or result field
- **THEN** system SHALL serialize dict to JSON string using json.dumps()
- **AND** system SHALL store JSON string in TEXT column

#### Scenario: Deserialize JSON on select
- **WHEN** reading config or result field
- **THEN** system SHALL deserialize JSON string to dict using json.loads()
- **AND** system SHALL handle NULL values (return None or empty dict)
