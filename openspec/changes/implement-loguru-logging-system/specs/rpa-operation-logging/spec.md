# Capability: RPA Operation Logging

RPA 操作专用日志能力，记录浏览器操作、用户行为和业务流程的详细信息。

## ADDED Requirements

### Requirement: Log RPA browser operations

The system SHALL log all browser operations performed during RPA automation.

#### Scenario: Log browser launch
- **WHEN** RPA module launches browser
- **THEN** system logs browser launch event with INFO level
- **AND** includes: browser type (Chrome/Edge), version, window size, headless mode
- **AND** includes launch duration
- **AND** logs success or failure

#### Scenario: Log page navigation
- **WHEN** RPA navigates to new URL
- **THEN** system logs navigation event with DEBUG level
- **AND** includes: from_url, to_url, navigation method
- **AND** includes page load time
- **AND** logs success or failure

#### Scenario: Log element interaction
- **WHEN** RPA interacts with page element (click, input, wait)
- **THEN** system logs interaction with TRACE level
- **AND** includes: element selector, interaction type, element text/attributes
- **AND** includes wait time before interaction
- **AND** logs success or failure (with screenshot on failure)

#### Scenario: Log element search
- **WHEN** RPA searches for element on page
- **THEN** system logs search attempt with TRACE level
- **AND** includes: selector, search method, search timeout
- **AND** logs whether element was found
- **AND** logs element position if found

### Requirement: Log user authentication operations

The system SHALL log BOSS Zhipin authentication operations in detail.

#### Scenario: Log login process start
- **WHEN** user initiates BOSS Zhipin login
- **THEN** system logs login start with INFO level
- **AND** includes: timestamp, user IP (if available), browser session ID
- **AND** assigns unique login session ID for tracking

#### Scenario: Log browser opened for login
- **WHEN** browser opens to login page
- **THEN** system logs with INFO level
- **AND** includes: login URL, browser configuration
- **AND** sends WebSocket notification to frontend

#### Scenario: Log login waiting period
- **WHEN** system waits for user to complete login
- **THEN** system logs waiting status every 10 seconds with DEBUG level
- **AND** includes: current URL, elapsed time, remaining timeout
- **AND** sends WebSocket notification to frontend

#### Scenario: Log login success
- **WHEN** user completes login successfully
- **THEN** system logs success with INFO level
- **AND** includes: username (extracted), cookies saved, session ID
- **AND** includes login duration
- **AND** sends WebSocket success notification to frontend

#### Scenario: Log login failure
- **WHEN** login fails (timeout, browser closed, error)
- **THEN** system logs failure with ERROR level
- **AND** includes: failure reason, session ID, elapsed time
- **AND** includes error details and stack trace if exception
- **AND** sends WebSocket error notification to frontend

### Requirement: Log job search operations

The system SHALL log job search and scraping operations.

#### Scenario: Log search criteria
- **WHEN** RPA performs job search
- **THEN** system logs search criteria with INFO level
- **AND** includes: keywords, city, experience, education, salary range
- **AND** includes search timestamp

#### Scenario: Log job scraping progress
- **WHEN** RPA scrapes job listings
- **THEN** system logs progress every 10 jobs with INFO level
- **AND** includes: jobs scraped, total jobs found, current page
- **AND** sends WebSocket notification to frontend

#### Scenario: Log individual job extraction
- **WHEN** RPA extracts job details
- **THEN** system logs extraction with DEBUG level
- **AND** includes: job title, company, salary, URL
- **AND** logs extraction success or failure
- **AND** includes screenshot on failure

#### Scenario: Log search completion
- **WHEN** job search completes (success or failure)
- **THEN** system logs completion with INFO level
- **AND** includes: total jobs found, jobs saved, duration
- **AND** includes errors encountered during search

### Requirement: Log automated chat operations

The system SHALL log automated chat operations with HR.

#### Scenario: Log chat initiation
- **WHEN** RPA initiates chat with HR
- **THEN** system logs chat start with INFO level
- **AND** includes: HR name, job title, greeting template
- **AND** includes timestamp

#### Scenario: Log message sending
- **WHEN** RPA sends chat message
- **THEN** system logs message with INFO level
- **AND** includes: message content (truncated if long), send duration
- **AND** logs success or failure
- **AND** includes error details if failed

#### Scenario: Log chat response
- **WHEN** HR replies to message
- **THEN** system logs response with DEBUG level
- **AND** includes: response content (truncated), response time
- **AND** does NOT include sensitive personal information

#### Scenario: Log chat conversation completion
- **WHEN** chat session completes
- **THEN** system logs completion with INFO level
- **AND** includes: messages exchanged, duration, outcome
- **AND** logs if follow-up is scheduled

### Requirement: Log RPA errors and exceptions

The system SHALL log all RPA errors with full context for debugging.

#### Scenario: Log element not found error
- **WHEN** RPA cannot find expected element
- **THEN** system logs error with ERROR level
- **AND** includes: selector, search method, timeout, page URL
- **AND** includes screenshot of page
- **AND** includes page HTML snippet (if available)

#### Scenario: Log timeout error
- **WHEN** RPA operation times out
- **THEN** system logs timeout with WARNING level
- **AND** includes: operation type, timeout duration, last known state
- **AND** includes screenshot

#### Scenario: Log unexpected exception
- **WHEN** RPA encounters unexpected exception
- **THEN** system logs exception with ERROR level
- **AND** includes: exception type, message, stack trace
- **AND** includes: RPA module state, browser state
- **AND** includes screenshot

#### Scenario: Log retry attempts
- **WHEN** RPA retries failed operation
- **THEN** system logs retry with INFO level
- **AND** includes: operation, attempt number, max attempts
- **AND** includes previous error (if any)
- **AND** logs final success or failure

### Requirement: Log RPA performance metrics

The system SHALL log RPA performance metrics for monitoring and optimization.

#### Scenario: Log operation duration
- **WHEN** RPA operation completes
- **THEN** system logs duration with DEBUG level
- **AND** includes: operation type, duration in milliseconds
- **AND** logs warning if duration exceeds threshold (e.g., > 5s)

#### Scenario: Log resource usage
- **WHEN** RPA module reports resource usage
- **THEN** system logs resource usage with INFO level (hourly)
- **AND** includes: memory usage, CPU usage, browser memory
- **AND** logs warning if usage exceeds threshold

#### Scenario: Log success rate
- **WHEN** RPA module completes batch operation
- **THEN** system logs success rate with INFO level
- **AND** includes: total operations, successful, failed, success rate percentage
- **AND** logs warning if success rate < 90%

### Requirement: Support RPA log filtering and search

The system SHALL support filtering and searching RPA operation logs.

#### Scenario: Filter logs by operation type
- **WHEN** user filters logs by operation (login, search, chat)
- **THEN** system returns only logs for that operation type
- **AND** filter is case-insensitive
- **AND** supports multiple operation filters

#### Scenario: Search logs by session ID
- **WHEN** user searches logs by login session ID
- **THEN** system returns all logs for that session
- **AND** includes logs from all RPA modules for that session
- **AND** maintains chronological order

#### Scenario: Export RPA logs
- **WHEN** administrator requests RPA log export
- **THEN** system exports logs to file (CSV or JSON)
- **AND** includes: all RPA logs for specified time range
- **AND** includes all fields (timestamp, operation, details, status)
- **AND** supports filtering before export

### Requirement: Protect sensitive information in RPA logs

The system SHALL protect sensitive information while maintaining detailed logging.

#### Scenario: Filter personal information
- **WHEN** logging chat messages or user data
- **THEN** system masks sensitive fields (phone, email ID, full name)
- **AND** replaces values with `***` or generic placeholders
- **AND** preserves structure for debugging

#### Scenario: Filter cookie and session data
- **WHEN** logging cookie or session information
- **THEN** system masks actual cookie values
- **AND** logs only cookie name and domain
- **AND** does NOT log actual cookie content

#### Scenario: Log without exposing user credentials
- **WHEN** logging authentication operations
- **THEN** system does NOT log user password or verification code
- **AND** logs only that credentials were entered (not the values)
- **AND** logs success/failure of authentication
