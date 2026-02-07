# Capability: Real-Time Log Streaming

实时日志流传输能力，通过 WebSocket 将后端日志推送到前端展示。

## ADDED Requirements

### Requirement: Establish WebSocket connection for log streaming

The system SHALL establish WebSocket connection to stream logs to frontend.

#### Scenario: Accept WebSocket log connection
- **WHEN** frontend connects to `/ws/logs`
- **THEN** system accepts WebSocket connection
- **AND** authenticates connection (user must be logged in)
- **AND** sends connection confirmation message

#### Scenario: Reject unauthenticated connections
- **WHEN** unauthenticated client connects to `/ws/logs`
- **THEN** system rejects connection with error code 1008
- **AND** logs unauthorized connection attempt
- **AND** does not stream logs to unauthenticated client

#### Scenario: Handle multiple concurrent connections
- **WHEN** multiple authenticated clients connect to `/ws/logs`
- **THEN** system accepts all connections
- **AND** broadcasts logs to all connected clients
- **AND** maintains separate connection state per client

### Requirement: Stream logs in real-time

The system SHALL stream log messages to frontend in real-time.

#### Scenario: Send log to WebSocket on log event
- **WHEN** any log message is generated
- **THEN** system formats log as JSON
- **AND** sends log to WebSocket handler
- **AND** WebSocket handler pushes to connected clients

#### Scenario: Batch log messages for efficiency
- **WHEN** multiple logs are generated rapidly
- **THEN** system buffers logs in memory (max 100 messages)
- **AND** sends batch when buffer is full
- **AND** sends batch every 1 second even if buffer not full

#### Scenario: Filter logs by level before streaming
- **WHEN** configuration sets streaming level to WARNING
- **THEN** system only sends WARNING, ERROR, CRITICAL logs via WebSocket
- **AND** INFO and DEBUG logs are not streamed (but still written to file)
- **AND** reduces bandwidth and frontend processing

### Requirement: Handle WebSocket connection lifecycle

The system SHALL properly manage WebSocket connection lifecycle.

#### Scenario: Detect client disconnection
- **WHEN** client disconnects (closes browser, network issue)
- **THEN** system detects disconnection
- **AND** stops streaming logs to that client
- **AND** logs disconnection event

#### Scenario: Reconnect on connection loss
- **WHEN** WebSocket connection is lost temporarily
- **THEN** frontend attempts reconnection with exponential backoff
- **AND** system accepts reconnection
- **AND** system does not send backlog logs (only new logs)

#### Scenario: Graceful shutdown of streaming
- **WHEN** application is shutting down
- **THEN** system sends shutdown message to all connected clients
- **AND** closes WebSocket connections gracefully
- **AND** completes all pending log sends

### Requirement: Support log filtering and pagination

The system SHALL support filtering logs before streaming to frontend.

#### Scenario: Filter logs by module
- **WHEN** client specifies module filter (e.g., "rpa")
- **THEN** system only sends logs from that module
- **AND** other module logs are not streamed to that client

#### Scenario: Filter logs by level
- **WHEN** client specifies level filter (e.g., "ERROR")
- **THEN** system only sends logs at that level or higher
- **AND** lower level logs are not streamed

#### Scenario: Filter logs by keyword
- **WHEN** client specifies keyword search (e.g., "login")
- **THEN** system only sends logs containing that keyword
- **AND** logs without keyword are not streamed

#### Scenario: Send recent logs on connection
- **WHEN** client connects with "tail" parameter (e.g., last 100 logs)
- **THEN** system retrieves recent logs from memory cache
- **AND** sends these logs to client on connection
- **AND** then continues streaming new logs

### Requirement: Implement rate limiting for log streaming

The system SHALL implement rate limiting to prevent performance impact.

#### Scenario: Limit log streaming rate
- **WHEN** log generation rate exceeds 100 logs/second
- **THEN** system buffers excess logs
- **AND** sends logs at maximum rate of 100 logs/second
- **AND** logs buffering statistics

#### Scenario: Drop logs when buffer full
- **WHEN** log buffer exceeds 1000 messages
- **THEN** system drops oldest logs from buffer
- **AND** logs dropped log event
- **AND** continues accepting new logs

#### Scenario: Pause streaming on slow client
- **WHEN** client cannot keep up with log rate
- **THEN** system sends pause signal to client
- **AND** reduces streaming rate for that client
- **AND** other clients are unaffected

### Requirement: Provide log streaming control API

The system SHALL provide API to control log streaming behavior.

#### Scenario: Enable/disable streaming globally
- **WHEN** administrator calls API to disable streaming
- **THEN** system stops streaming logs to all clients
- **AND** logs continue to be written to file
- **AND** system sends notification to clients

#### Scenario: Adjust streaming level dynamically
- **WHEN** administrator calls API to change streaming level
- **THEN** system updates streaming level filter
- **AND** new level applies to all current and future connections
- **AND** system confirms level change

#### Scenario: Get streaming statistics
- **WHEN** administrator calls API for streaming stats
- **THEN** system returns: connected clients count, logs sent, buffer size, drop count
- **AND** statistics are calculated since application start or last reset
