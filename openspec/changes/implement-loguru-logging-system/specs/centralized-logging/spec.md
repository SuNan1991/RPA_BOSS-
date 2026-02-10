# Capability: Centralized Logging

统一的日志管理系统，提供全局日志配置、logger 工厂和日志级别管理。

## ADDED Requirements

### Requirement: Provide centralized logger configuration

The system SHALL provide a centralized logging manager that configures all loggers in the application.

#### Scenario: Initialize global logging on application startup
- **WHEN** application starts
- **THEN** system creates LogManager instance
- **AND** configures global loguru logger with handlers (file, console, WebSocket)
- **AND** sets default log level to INFO
- **AND** removes default loguru handler

#### Scenario: Get module-specific logger
- **WHEN** code calls `LogManager.get_logger(__name__)`
- **THEN** system returns a logger bound to module name
- **AND** logger automatically includes module name in all log messages
- **AND** logger inherits global configuration (handlers, level, format)

#### Scenario: Configure multiple log handlers
- **WHEN** LogManager sets up logging
- **THEN** system adds file handler (logs to file with rotation)
- **AND** system adds console handler (colored output to terminal)
- **AND** system adds WebSocket handler (sends logs to frontend)
- **AND** all handlers receive same log messages

### Requirement: Support dynamic log level adjustment

The system SHALL support adjusting log levels at runtime without restart.

#### Scenario: Change global log level
- **WHEN** administrator calls API to change global log level
- **THEN** system updates global logger level
- **AND** all module loggers inherit new level (unless overridden)
- **AND** system returns new level

#### Scenario: Change module-specific log level
- **WHEN** administrator calls API to change specific module level
- **THEN** system updates that module's logger level
- **AND** other module loggers are unaffected
- **AND** system returns confirmation

#### Scenario: Load log level from configuration file
- **WHEN** application starts
- **THEN** system reads log level from config/logging_config.yaml
- **AND** applies levels to global and module-specific loggers
- **AND** uses INFO as default if config not found

### Requirement: Provide unified logging API

The system SHALL provide simple API for logging operations.

#### Scenario: Log at different levels
- **WHEN** code calls `logger.trace()`, `logger.debug()`, `logger.info()`, etc.
- **THEN** system formats and outputs log message
- **AND** includes timestamp, module name, level, and message
- **AND** routes to all configured handlers

#### Scenario: Log with context information
- **WHEN** code calls `logger.bind(context=value).info()`
- **THEN** system includes context in log output
- **AND** context appears in all handlers (file, WebSocket, console)
- **AND** context persists for subsequent log calls (until unbind)

#### Scenario: Log exceptions automatically
- **WHEN** code uses `logger.exception()` or `logger.opt()`
- **THEN** system automatically captures exception info
- **AND** includes exception type, message, and stack trace
- **AND** formats stack trace in readable format

### Requirement: Support log filtering and formatting

The system SHALL support filtering sensitive information and custom formatting.

#### Scenario: Filter sensitive information
- **WHEN** log message contains sensitive fields (password, token, cookie, secret)
- **THEN** system replaces field values with `***`
- **AND** preserves log message structure
- **AND** logs filtering event for audit

#### Scenario: Format log messages
- **WHEN** log is written to file
- **THEN** system uses text format: `[<timestamp>] [<level>] [<module>] <message>`
- **AND** includes exception trace if present
- **AND** writes to file with UTF-8 encoding

#### Scenario: Format logs for frontend
- **WHEN** log is sent to WebSocket handler
- **THEN** system serializes to JSON format
- **AND** includes fields: timestamp, level, module, message, exception
- **AND** ready for frontend consumption

### Requirement: Monitor logging system health

The system SHALL monitor logging system health and alert on issues.

#### Scenario: Detect log file write failures
- **WHEN** file handler fails to write (disk full, permission denied)
- **THEN** system logs error to console
- **AND** system sends alert to administrator
- **AND** system continues with other handlers

#### Scenario: Detect WebSocket disconnection
- **WHEN** WebSocket handler cannot push logs
- **THEN** system buffers logs in memory
- **AND** system retries connection every 5 seconds
- **AND** system alerts when buffer exceeds 1000 messages

#### Scenario: Monitor log file size
- **WHEN** log file directory size exceeds threshold (1GB)
- **THEN** system sends warning to administrator
- **AND** system suggests cleaning old logs
