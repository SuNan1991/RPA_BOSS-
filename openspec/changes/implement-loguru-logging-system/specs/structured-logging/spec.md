# Capability: Structured Logging

结构化日志能力，支持 JSON 格式输出和字段提取，便于日志分析和监控。

## ADDED Requirements

### Requirement: Support structured log output

The system SHALL support structured log format with fields and values.

#### Scenario: Output logs in JSON format
- **WHEN** JSON format is enabled in configuration
- **THEN** system outputs logs as JSON objects
- **AND** JSON includes: timestamp, level, module, message, context, exception
- **AND** JSON is written as single line per log entry

#### Scenario: Add custom fields to logs
- **WHEN** code logs with extra fields using `logger.bind(field=value)`
- **THEN** system includes these fields in log output
- **AND** fields appear in JSON log as top-level keys
- **AND** fields are included in all handler outputs (file, WebSocket)

#### Scenario: Serialize complex objects in logs
- **WHEN** code logs complex object (dict, list, custom class)
- **THEN** system serializes object to JSON
- **AND** nested structures are preserved
- **AND** unserializable objects are converted to string representation

### Requirement: Extract and index log fields

The system SHALL enable log field extraction for analysis.

#### Scenario: Extract timestamp field
- **WHEN** log is written in JSON format
- **THEN** system includes `@timestamp` field in ISO 8601 format
- **AND** timestamp is sortable and queryable
- **AND** timezone is UTC or system-configured timezone

#### Scenario: Extract level field
- **WHEN** log is written in JSON format
- **THEN** system includes `level` field with string value (INFO, ERROR, etc.)
- **AND** level is filterable in log analysis tools
- **AND** level is normalized across all modules

#### Scenario: Extract module/function fields
- **WHEN** log is written in JSON format
- **THEN** system includes `module` field with module name
- **AND** system includes `function` field with function name if available
- **AND** system includes `line` field with line number if available

#### Scenario: Extract context fields
- **WHEN** log includes custom context (user_id, request_id, etc.)
- **THEN** system includes these as top-level fields in JSON
- **AND** fields are queryable in log analysis tools
- **AND** field names follow snake_case convention

### Requirement: Support log aggregation

The system SHALL support log aggregation for external systems.

#### Scenario: Export logs to ELK stack
- **WHEN** ELK integration is enabled
- **THEN** system sends JSON logs to Elasticsearch
- **AND** uses index pattern `boss-rpa-logs-YYYY-MM-DD`
- **AND** enables Kibana visualization

#### Scenario: Export logs to Loki
- **WHEN** Loki integration is enabled
- **THEN** system sends logs to Loki via HTTP API
- **AND** includes labels: module, level, environment
- **AND** enables Grafana visualization

#### Scenario: Format logs for filebeat
- **WHEN** filebeat is configured to read log files
- **THEN** system outputs logs in JSON format
- **AND** filebeat can parse and forward to logstash/elasticsearch
- **AND** no additional parsing is needed

### Requirement: Preserve human-readable format

The system SHALL support both JSON and human-readable text formats.

#### Scenario: Output logs in text format
- **WHEN** JSON format is disabled (default)
- **THEN** system outputs logs in human-readable text format
- **AND** format: `[2025-02-07 10:30:45] [INFO] [module] Message`
- **AND** exception traces are formatted with indentation

#### Scenario: Colorize console output
- **WHEN** logs are written to console
- **THEN** system applies color coding based on level
- **AND** ERROR/CRITICAL are red, WARNING is yellow, INFO is cyan, SUCCESS is green
- **AND** color codes work in terminal and some log viewers

#### Scenario: Switch between formats
- **WHEN** configuration changes format (text <-> JSON)
- **THEN** system starts outputting in new format for new logs
- **AND** existing logs remain in their original format
- **AND** system logs format change event

### Requirement: Validate structured log schema

The system SHALL validate structured log fields and values.

#### Scenario: Validate required fields
- **WHEN** log is written in JSON format
- **THEN** system ensures required fields exist (timestamp, level, message)
- **AND** system adds missing required fields with default values
- **AND** system logs validation warning

#### Scenario: Sanitize field values
- **WHEN** log field value contains special characters or newlines
- **THEN** system escapes or removes problematic characters
- **AND** preserves single-line JSON format
- **AND** does not break log parsing

#### Scenario: Truncate excessive field values
- **WHEN** log field value exceeds maximum length (10KB)
- **THEN** system truncates value to 10KB
- **AND** adds ellipsis (...) to indicate truncation
- **AND** logs truncation event

### Requirement: Support log query and analysis

The system SHALL enable querying structured logs via API.

#### Scenario: Query logs by field
- **WHEN** client requests logs with field filter (e.g., `{"level": "ERROR"}`)
- **THEN** system searches log files for matching logs
- **AND** returns matching log entries as JSON array
- **AND** supports pagination (limit, offset)

#### Scenario: Query logs by time range
- **WHEN** client requests logs with time range filter
- **THEN** system filters logs by timestamp
- **AND** returns logs within range
- **AND** supports ISO 8601 timestamps

#### Scenario: Aggregate logs by field
- **WHEN** client requests aggregation (e.g., count by level)
- **THEN** system scans logs and calculates aggregation
- **AND** returns aggregation result as JSON
- **AND** supports common aggregations: count, sum, avg
