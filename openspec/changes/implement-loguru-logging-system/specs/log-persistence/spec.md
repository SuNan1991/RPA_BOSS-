# Capability: Log Persistence

日志持久化能力，负责日志文件的创建、轮转、压缩和清理。

## ADDED Requirements

### Requirement: Create and manage log files

The system SHALL create log files in dedicated directory with proper management.

#### Scenario: Create log directory
- **WHEN** application starts
- **THEN** system creates `backend/logs/` directory if not exists
- **AND** sets directory permissions to 750 (owner rwx, group rx, other rx)
- **AND** verifies write access

#### Scenario: Create application log file
- **WHEN** first log is written
- **THEN** system creates `backend/logs/app_<date>.log` file
- **AND** file includes current date in YYYY-MM-DD format
- **AND** system sets file permissions to 640 (owner rw, group r)

#### Scenario: Create error-specific log file
- **WHEN** configuration enables error log separation
- **THEN** system creates `backend/logs/app_error_<date>.log` file
- **AND** only ERROR and CRITICAL level logs are written to this file
- **AND** other level logs go to main application log file

### Requirement: Implement log rotation

The system SHALL implement automatic log rotation based on size and time.

#### Scenario: Rotate log file by size
- **WHEN** log file size exceeds 100MB
- **THEN** system closes current file
- **AND** creates new file with timestamp
- **AND** renames old file to `app_<date>_<index>.log`

#### Scenario: Rotate log file by time
- **WHEN** date changes (midnight)
- **THEN** system creates new log file with new date
- **AND** old file remains in directory with previous date

#### Scenario: Handle rotation during active writing
- **WHEN** file is rotated
- **THEN** system completes writing current log message to old file
- **AND** switches to new file for next log message
- **AND** no log messages are lost during rotation

### Requirement: Compress old log files

The system SHALL compress old log files to save disk space.

#### Scenario: Compress rotated logs
- **WHEN** log file is rotated (not actively written)
- **THEN** system compresses file using gzip
- **AND** compressed file has `.gz` extension
- **AND** system deletes original uncompressed file after successful compression

#### Scenario: Compress logs during low activity
- **WHEN** application has low CPU usage
- **THEN** system scans for uncompressed log files older than 1 hour
- **AND** compresses these files in background
- **AND** does not impact application performance

#### Scenario: Verify compression integrity
- **WHEN** compressing log file
- **THEN** system verifies compressed file integrity
- **AND** keeps original file if compression fails
- **AND** logs compression error

### Requirement: Implement log retention and cleanup

The system SHALL automatically clean up old log files based on retention policy.

#### Scenario: Delete expired log files
- **WHEN** log file is older than retention period (default 30 days)
- **THEN** system deletes both compressed and uncompressed files
- **AND** system keeps at least 7 days of logs regardless of retention period
- **AND** logs cleanup event for audit

#### Scenario: Monitor disk space
- **WHEN** log directory size exceeds threshold (1GB)
- **THEN** system sends alert to administrator
- **AND** system suggests reducing retention period
- **AND** system calculates space that would be freed by cleanup

#### Scenario: Manual cleanup trigger
- **WHEN** administrator calls cleanup API
- **THEN** system scans for files older than specified days
- **AND** deletes these files
- **AND** returns list of deleted files and space freed

### Requirement: Support configurable retention policies

The system SHALL support different retention policies per log type.

#### Scenario: Configure application log retention
- **WHEN** configuration file specifies `app_logs_retention: 30 days`
- **THEN** system keeps application logs for 30 days
- **AND** system deletes application logs older than 30 days

#### Scenario: Configure error log retention
- **WHEN** configuration file specifies `error_logs_retention: 90 days`
- **THEN** system keeps error logs for 90 days (longer retention)
- **AND** system deletes error logs older than 90 days

#### Scenario: Override retention policy
- **WHEN** administrator calls API with custom retention period
- **THEN** system temporarily applies new retention period
- **AND** system logs retention change event
- **AND** system reverts to configured retention on restart (unless saved)

### Requirement: Ensure log file integrity

The system SHALL ensure log files are written correctly and can be recovered.

#### Scenario: Flush log buffers periodically
- **WHEN** 10 seconds have passed since last flush
- **THEN** system flushes log buffer to disk
- **AND** ensures all cached logs are written
- **AND** continues accepting new logs during flush

#### Scenario: Flush on application shutdown
- **WHEN** application is shutting down
- **THEN** system calls `logger.complete()` to flush all handlers
- **AND** system waits for all logs to be written
- **AND** system exits only after flush complete

#### Scenario: Handle disk full errors
- **WHEN** disk write fails due to insufficient space
- **THEN** system logs error to console
- **AND** system attempts to free space (compress old logs)
- **AND** system continues running with console-only logging
