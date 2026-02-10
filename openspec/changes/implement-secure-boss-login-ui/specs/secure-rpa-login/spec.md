# Capability: Secure RPA Login

安全的 RPA 辅助登录能力。通过用户辅助的方式实现安全登录，避免自动化检测。

## ADDED Requirements

### Requirement: Launch RPA browser to BOSS Zhipin login page

The system SHALL launch a browser instance using DrissionPage and navigate to BOSS Zhipin login page.

#### Scenario: Successful browser launch
- **WHEN** user initiates login process
- **THEN** system creates new browser instance with anti-detection configuration
- **AND** navigates to https://login.zhipin.com/
- **AND** browser window is visible (not headless)
- **AND** browser window size is 1920x1080 or user's screen resolution
- **AND** system sends WebSocket message `browser_opened` to frontend

#### Scenario: Browser launch failure
- **WHEN** browser fails to launch (Chrome not installed, permission error)
- **THEN** system logs error with detailed message
- **AND** sends WebSocket message `browser_launch_failed` to frontend
- **AND** frontend displays error message "浏览器启动失败，请检查 Chrome 是否已安装"
- **AND** login button returns to normal state

#### Scenario: Multiple browser launch attempts
- **WHEN** user clicks login button while browser is already open
- **THEN** system closes existing browser instance
- **AND** launches new browser instance
- **AND** logs warning "Browser already open, restarting..."

### Requirement: Implement anti-detection browser configuration

The system SHALL configure browser with anti-detection settings to avoid BOSS Zhipin's automated bot detection.

#### Scenario: Apply anti-detection configuration
- **WHEN** system creates browser instance
- **THEN** system sets User-Agent to real Chrome browser string
- **AND** disables automation flags (--disable-blink-features=AutomationControlled)
- **AND** excludes automation switches (--exclude-switches=enable-automation)
- **AND** hides infobars (--disable-infobars)
- **AND** sets navigator.webdriver to undefined via JavaScript injection
- **AND** configures real plugins array (not empty)
- **AND** sets window size to realistic desktop resolution

#### Scenario: Randomize User-Agent
- **WHEN** system creates browser instance
- **THEN** system randomly selects User-Agent from predefined list
- **AND** list includes Windows and Mac user agents
- **AND** uses different user agent for each session to avoid pattern detection

#### Scenario: Verify anti-detection effectiveness
- **WHEN** browser is launched
- **THEN** system executes JavaScript to check navigator.webdriver
- **AND** verifies value is undefined (not true)
- **AND** logs warning if detection fails
- **AND** continues with login process but records potential risk

### Requirement: Wait for user to complete login manually

The system SHALL wait for user to manually scan QR code or enter credentials to complete login.

#### Scenario: Monitor login status by checking URL
- **WHEN** browser is on login page
- **THEN** system polls browser current URL every 2 seconds
- **AND** checks if URL has changed from login.zhipin.com to dashboard or home page
- **AND** when URL change is detected, assumes login is successful
- **AND** proceeds to extract cookies

#### Scenario: Monitor login status by checking specific element
- **WHEN** URL-based detection is not reliable
- **THEN** system checks for presence of user avatar element on page
- **AND** checks for presence of user name element
- **AND** when both elements are found, assumes login is successful

#### Scenario: Send status updates during waiting period
- **WHEN** system is waiting for user to complete login
- **THEN** system sends WebSocket message `waiting_for_login` every 5 seconds
- **AND** message includes current URL for debugging
- **AND** frontend updates instruction text to remind user to scan QR code

#### Scenario: User cancels login by closing browser
- **WHEN** user manually closes browser window before completing login
- **THEN** system detects browser closure via DrissionPage
- **AND** sends WebSocket message `browser_closed` to frontend
- **AND** frontend displays message "浏览器已关闭，登录已取消"
- **AND** login button returns to normal state

### Requirement: Extract and save cookies after successful login

The system SHALL extract cookies from browser after successful login and save them to database.

#### Scenario: Successful cookie extraction
- **WHEN** system detects successful login
- **THEN** system extracts all cookies from browser session
- **AND** filters cookies for domain `.zhipin.com`
- **AND** includes essential cookies (session token, user ID, etc.)
- **AND** encrypts cookies using Fernet encryption
- **AND** saves encrypted cookies to `sessions` table in SQLite
- **AND** sends WebSocket message `login_successful` to frontend

#### Scenario: Extract user information from page
- **WHEN** system detects successful login
- **THEN** system extracts user information from BOSS Zhipin page
- **AND** extracts username from user profile element
- **AND** extracts avatar URL if available
- **AND** saves user information to `sessions` table along with cookies
- **AND** sends user information to frontend via WebSocket

#### Scenario: Cookie extraction failure
- **WHEN** system fails to extract cookies (browser crashed, permission error)
- **THEN** system logs error with stack trace
- **AND** sends WebSocket message `cookie_extraction_failed` to frontend
- **AND** frontend displays error message "登录信息保存失败，请重试"
- **AND** closes browser instance

#### Scenario: Cookie encryption failure
- **WHEN** system fails to encrypt cookies (key not available, encryption error)
- **THEN** system logs critical error
- **AND** does not save cookies to database
- **AND** sends WebSocket message `encryption_failed` to frontend
- **AND** frontend displays error message "系统加密错误，请联系管理员"

### Requirement: Implement login timeout mechanism

The system SHALL automatically close browser and terminate login process if user does not complete login within 5 minutes.

#### Scenario: Timeout after 5 minutes
- **WHEN** user does not complete login within 5 minutes
- **THEN** system automatically closes browser instance
- **AND** sends WebSocket message `login_timeout` to frontend
- **AND** frontend displays error message "登录超时（5分钟），请重试"
- **AND** login button returns to normal state
- **AND** logs timeout event for monitoring

#### Scenario: Reset timeout on user activity
- **WHEN** system detects browser activity (URL change, mouse movement)
- **THEN** system resets timeout timer to 5 minutes
- **AND** continues waiting for login completion
- **AND** logs timeout reset event

#### Scenario: Show countdown timer in frontend
- **WHEN** login process is active
- **THEN** frontend displays countdown timer (5:00, 4:59, 4:58, ...)
- **AND** timer updates every second
- **AND** timer shows warning color when less than 1 minute remains
- **AND** timer stops when login is successful or browser is closed

### Requirement: Close browser instance after login completion

The system SHALL close browser instance after successful cookie extraction to free system resources.

#### Scenario: Normal browser closure
- **WHEN** system has successfully extracted cookies and user information
- **THEN** system closes browser instance gracefully
- **AND** releases all system resources (memory, file handles)
- **AND** sends WebSocket message `browser_closed` to frontend
- **AND** logs browser closure event

#### Scenario: Browser closure failure
- **WHEN** system fails to close browser (process already killed, system error)
- **THEN** system logs warning with error details
- **AND** forces browser process termination using system command
- **AND** continues with cleanup process
- **AND** does not affect user experience (cookies already saved)

#### Scenario: Keep browser open for debugging (optional)
- **WHEN** system is in development mode (DEBUG=true)
- **THEN** system does NOT close browser after login
- **AND** displays message "浏览器已保持打开，方便调试"
- **AND** allows developer to inspect browser state

### Requirement: Implement WebSocket real-time status push

The system SHALL push real-time login status updates to frontend via WebSocket connection.

#### Scenario: Push login status updates
- **WHEN** login process state changes (e.g., browser opened, waiting for login, login successful)
- **THEN** system sends WebSocket message with status update
- **AND** message includes status code (e.g., `browser_opened`, `waiting_for_login`, `login_successful`)
- **AND** message includes timestamp
- **AND** message includes additional data (URL, user info) if applicable
- **AND** frontend updates UI based on received status

#### Scenario: Handle WebSocket connection errors
- **WHEN** WebSocket connection is lost during login process
- **THEN** system continues with login process in background
- **AND** logs WebSocket disconnection event
- **AND** frontend automatically attempts reconnection
- **AND** after reconnection, frontend requests current login status via `/api/auth/status`

#### Scenario: Broadcast to multiple connected clients
- **WHEN** multiple browser tabs are connected to WebSocket
- **THEN** system broadcasts status updates to all connected clients
- **AND** all tabs show consistent login status
- **AND** all tabs update UI simultaneously

### Requirement: Restore session from saved cookies

The system SHALL restore user session from previously saved cookies when application starts.

#### Scenario: Auto-login on application startup
- **WHEN** backend application starts
- **THEN** system queries `sessions` table for most recent valid session
- **AND** checks if session is not expired (created_at < 30 days ago)
- **AND** decrypts cookies using Fernet decryption
- **AND** loads cookies into browser instance (if browser is needed)
- **AND** sends WebSocket message `session_restored` to frontend
- **AND** frontend displays authenticated page with user information

#### Scenario: No valid session found
- **WHEN** backend application starts and no valid session exists
- **THEN** system sends WebSocket message `no_session_found` to frontend
- **AND** frontend displays landing page with login button
- **AND** does not attempt to restore session

#### Scenario: Session expired
- **WHEN** system finds session but it is expired (> 30 days old)
- **THEN** system deletes expired session from database
- **AND** sends WebSocket message `session_expired` to frontend
- **AND** frontend displays landing page with login button
- **AND** may show message "会话已过期，请重新登录"

#### Scenario: Cookie decryption failure
- **WHEN** system fails to decrypt cookies (key changed, corrupted data)
- **THEN** system logs error with details
- **AND** deletes invalid session from database
- **AND** sends WebSocket message `session_restore_failed` to frontend
- **AND** frontend displays landing page with login button

### Requirement: Implement session cleanup and logout

The system SHALL provide logout functionality that clears cookies and invalidates session.

#### Scenario: User-initiated logout
- **WHEN** user clicks logout button in frontend
- **THEN** system receives `/api/auth/logout` request
- **AND** deletes current session from `sessions` table
- **AND** if browser instance is open, closes it
- **AND** clears all cookies from memory
- **AND** sends WebSocket message `logged_out` to frontend
- **AND** frontend redirects to landing page

#### Scenario: Automatic session cleanup
- **WHEN** system detects multiple old sessions (> 30 days)
- **THEN** system deletes old sessions from database
- **AND** keeps only the most recent session
- **AND** logs cleanup event

#### Scenario: Logout all sessions (admin feature)
- **WHEN** administrator requests to logout all sessions (e.g., `/api/auth/logout-all`)
- **THEN** system deletes all sessions from database
- **AND** closes all browser instances if any
- **AND** sends WebSocket message `all_sessions_logged_out` to all connected clients
- **AND** all clients redirect to landing page

### Requirement: Log login events for monitoring and debugging

The system SHALL log all login-related events to database and log files.

#### Scenario: Log successful login
- **WHEN** user successfully completes login
- **THEN** system inserts record into `login_logs` table
- **AND** record includes: timestamp, username, success=true, ip_address, user_agent
- **AND** logs info message to application log file

#### Scenario: Log failed login attempt
- **WHEN** login process fails (timeout, browser closed, error)
- **THEN** system inserts record into `login_logs` table
- **AND** record includes: timestamp, username=null, success=false, failure_reason, error_details
- **AND** logs warning message to application log file

#### Scenario: Log browser events
- **WHEN** browser events occur (launch, close, crash)
- **THEN** system logs event with timestamp and event type
- **AND** includes diagnostic information (browser PID, window size, URL)
- **AND** logs to application log file (not database)

#### Scenario: Query login logs (admin feature)
- **WHEN** administrator requests login history (e.g., `/api/auth/logs`)
- **THEN** system returns list of recent login events from `login_logs` table
- **AND** supports pagination (limit, offset)
- **AND** supports filtering by date range and success status
- **AND** requires authentication (admin only)

### Requirement: Validate browser prerequisites before launch

The system SHALL validate browser prerequisites before launching browser instance.

#### Scenario: Check Chrome installation
- **WHEN** user initiates login process
- **THEN** system checks if Chrome browser is installed
- **AND** checks if Chrome executable exists at standard path
- **AND** if Chrome is not found, returns error "Chrome 浏览器未安装，请先安装 Chrome"
- **AND** login process is aborted

#### Scenario: Check browser version compatibility
- **WHEN** Chrome browser is found
- **THEN** system checks Chrome version (must be >= 90)
- **AND** if version is too old, returns error "Chrome 版本过低，请升级到最新版本"
- **AND** login process is aborted

#### Scenario: Check system resources
- **WHEN** user initiates login process
- **THEN** system checks available system memory (must be > 512MB free)
- **AND** checks if another browser instance is already running
- **AND** if resources insufficient, returns error "系统资源不足，请关闭其他程序后重试"
- **AND** login process is aborted

### Requirement: Implement browser instance lifecycle management

The system SHALL manage browser instance lifecycle to prevent resource leaks.

#### Scenario: Singleton browser pattern
- **WHEN** system is running
- **THEN** only one browser instance is allowed at a time
- **AND** if new login is initiated while browser is open, close existing browser first
- **AND** use singleton pattern for BrowserManager class

#### Scenario: Automatic cleanup on application shutdown
- **WHEN** backend application is shutting down (SIGTERM, SIGINT)
- **THEN** system gracefully closes browser instance
- **AND** releases all resources
- **AND** logs shutdown event
- **AND** exits cleanly

#### Scenario: Monitor browser health
- **WHEN** browser instance is running
- **THEN** system checks browser process health every 10 seconds
- **AND** if browser process is dead but system thinks it's alive, update state
- **AND** if browser is unresponsive (no URL change for 60 seconds), log warning
- **AND** if browser is crashed, attempt to restart or cleanup

### Requirement: Prevent concurrent login attempts

The system SHALL prevent multiple concurrent login attempts from the same user.

#### Scenario: Reject login while already in progress
- **WHEN** user clicks login button while login process is already active
- **THEN** system rejects new login request
- **AND** returns error "登录正在进行中，请稍候"
- **AND** login button remains disabled
- **AND** frontend does not send duplicate request

#### Scenario: Handle multiple browser tabs
- **WHEN** user has multiple browser tabs open
- **THEN** all tabs share the same login state via WebSocket
- **AND** if one tab initiates login, other tabs show "登录进行中" state
- **AND** when login completes, all tabs update to authenticated state

#### Scenario: Clear login state after completion or failure
- **WHEN** login process completes (success or failure)
- **THEN** system resets login state to idle
- **AND** allows new login attempt
- **AND** login button becomes enabled again
