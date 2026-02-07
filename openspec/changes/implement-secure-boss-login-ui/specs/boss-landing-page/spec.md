# Capability: Boss Landing Page

首页/登录引导页能力。提供极简的 Landing Page，展示系统介绍和账号状态，包含登录按钮。

## ADDED Requirements

### Requirement: Display system landing page with account status

The system SHALL display a minimal landing page that shows current system status and account information.

#### Scenario: View landing page when not authenticated
- **WHEN** user accesses the application without authentication
- **THEN** system displays landing page with login button
- **AND** shows "未登录" (Not Logged In) status
- **AND** displays system introduction text
- **AND** shows connection status indicator as disconnected

#### Scenario: View landing page when authenticated
- **WHEN** user has successfully logged in
- **THEN** system displays authenticated page with account information
- **AND** shows username from BOSS Zhipin account
- **AND** displays user avatar if available
- **AND** shows connection duration time
- **AND** displays logout button instead of login button

### Requirement: Provide login button to initiate RPA login process

The system SHALL provide a prominent login button that triggers the RPA-assisted login flow.

#### Scenario: Click login button when not authenticated
- **WHEN** user clicks the login button
- **THEN** system sends request to `/api/auth/login` endpoint
- **AND** button shows loading state with spinner animation
- **AND** button displays "正在启动浏览器..." (Starting browser...)
- **AND** button is disabled during the login process

#### Scenario: Login button state updates with RPA status
- **WHEN** RPA browser successfully opens
- **THEN** button text changes to "请扫码登录" (Please scan to login)
- **AND** displays QR code scanning instruction
- **AND** shows countdown timer for login timeout (5 minutes)

#### Scenario: Login button returns to normal after timeout
- **WHEN** login process times out (5 minutes)
- **THEN** button returns to normal state
- **AND** shows error message "登录超时，请重试" (Login timeout, please retry)
- **AND** button is enabled for retry

### Requirement: Display account information card

The system SHALL display an account information card with user details when authenticated.

#### Scenario: Display full account information
- **WHEN** user is authenticated
- **THEN** system displays account card with:
  - Username from BOSS Zhipin account
  - User avatar (or default placeholder if unavailable)
  - Account status indicator (Connected/Disconnected)
  - Connection duration (e.g., "已连接 2小时 30分")
  - Last login timestamp

#### Scenario: Display placeholder when avatar unavailable
- **WHEN** user avatar is not available from BOSS Zhipin
- **THEN** system displays default placeholder with first letter of username
- **AND** placeholder uses primary color #5C6BC0 as background

#### Scenario: Hide account card when not authenticated
- **WHEN** user is not authenticated
- **THEN** system does not display account information card
- **AND** only shows landing page with login button

### Requirement: Provide real-time connection status indicator

The system SHALL display a real-time connection status indicator that shows WebSocket connection health.

#### Scenario: Show connected status
- **WHEN** WebSocket connection is established and healthy
- **THEN** system displays green status indicator (circle icon)
- **AND** shows tooltip "连接正常" (Connected)
- **AND** indicator pulses every 2 seconds to indicate active connection

#### Scenario: Show disconnected status
- **WHEN** WebSocket connection is lost or failed
- **THEN** system displays red status indicator
- **AND** shows tooltip "连接断开" (Disconnected)
- **AND** indicator shows static (non-pulsing) state
- **AND** system automatically attempts reconnection in background

#### Scenario: Show connecting status
- **WHEN** system is attempting to establish WebSocket connection
- **THEN** system displays yellow status indicator
- **AND** shows tooltip "正在连接..." (Connecting...)
- **AND** indicator shows animation (spinning or pulsing)

### Requirement: Support light/dark theme toggle

The system SHALL provide a theme toggle button that allows users to switch between light and dark modes.

#### Scenario: Toggle to dark mode
- **WHEN** user clicks theme toggle button
- **THEN** system switches to dark mode
- **AND** background changes to dark (#1a1a1a or similar)
- **AND** text changes to light color
- **AND** glass morphism effect adjusts (dark glass background)
- **AND** theme preference is saved to localStorage

#### Scenario: Toggle to light mode
- **WHEN** user clicks theme toggle button while in dark mode
- **THEN** system switches to light mode
- **AND** background changes to light color
- **AND** text changes to dark color
- **AND** glass morphism effect adjusts (light glass background)
- **AND** theme preference is saved to localStorage

#### Scenario: Respect system theme preference on first visit
- **WHEN** user visits application for the first time
- **THEN** system detects user's system theme preference
- **AND** automatically applies light or dark mode based on system setting
- **AND** uses `prefers-color-scheme` media query

#### Scenario: Maintain theme preference across sessions
- **WHEN** user returns to application after closing
- **THEN** system loads saved theme preference from localStorage
- **AND** applies the previously selected theme
- **AND** does not show flicker during initial load

### Requirement: Display system introduction and instructions

The system SHALL display clear system introduction and user instructions on the landing page.

#### Scenario: Show system introduction
- **WHEN** user views landing page
- **THEN** system displays:
  - Application name ("BOSS 直聘 RPA 助手")
  - Brief description ("安全的 BOSS 直聘自动化工具")
  - Key features list (max 3 items)
- **AND** text uses primary color #5C6BC0 for emphasis

#### Scenario: Show login instructions
- **WHEN** user clicks login button
- **THEN** system displays step-by-step instructions:
  1. "系统将自动打开 BOSS 直聘登录页"
  2. "请使用 BOSS 直聘 App 扫码登录"
  3. "登录成功后自动保存账号信息"
- **AND** instructions use large, readable font size
- **AND** instructions support dark mode

### Requirement: Implement responsive design for desktop and mobile

The system SHALL display landing page correctly on desktop and mobile devices.

#### Scenario: Display on desktop screen (> 1024px)
- **WHEN** user accesses landing page on desktop
- **THEN** system displays content centered horizontally
- **AND** uses maximum width of 1200px for main content
- **AND** shows account card and login button side by side (if authenticated)

#### Scenario: Display on tablet screen (768px - 1024px)
- **WHEN** user accesses landing page on tablet
- **THEN** system adjusts layout to single column
- **AND** reduces padding and margins
- **AND** maintains readable font size

#### Scenario: Display on mobile screen (< 768px)
- **WHEN** user accesses landing page on mobile
- **THEN** system uses full-width layout
- **AND** stacks all elements vertically
- **AND** adjusts font sizes for readability
- **AND** touch targets are at least 44x44 pixels

### Requirement: Provide logout functionality

The system SHALL provide a logout button that clears the current session and returns to landing page.

#### Scenario: Click logout button
- **WHEN** authenticated user clicks logout button
- **THEN** system sends request to `/api/auth/logout` endpoint
- **AND** shows confirmation dialog "确定要退出登录吗？" (Confirm logout?)
- **AND** if confirmed, clears local authentication state
- **AND** redirects to landing page
- **AND** shows success message "已退出登录" (Logged out successfully)

#### Scenario: Cancel logout
- **WHEN** user clicks logout button but cancels confirmation
- **THEN** system remains on authenticated page
- **AND** does not clear authentication state
- **AND** does not send logout request to server

#### Scenario: Handle logout error
- **WHEN** logout request fails (network error, server error)
- **THEN** system displays error message "退出登录失败，请重试" (Logout failed, please retry)
- **AND** remains on authenticated page
- **AND** allows user to retry logout

### Requirement: Implement glassmorphism visual design

The system SHALL implement glassmorphism design style with backdrop blur and transparency effects.

#### Scenario: Apply glassmorphism to cards
- **WHEN** system displays any card component (account card, login card)
- **THEN** card background uses semi-transparent color (rgba(255,255,255,0.7) for light mode)
- **AND** applies backdrop-filter: blur(20px) for frosted glass effect
- **AND** adds subtle border (1px solid rgba(255,255,255,0.18))
- **AND** adds box-shadow for depth

#### Scenario: Apply glassmorphism in dark mode
- **WHEN** system is in dark mode
- **THEN** card background uses dark semi-transparent color (rgba(0,0,0,0.7))
- **AND** applies same backdrop-filter blur effect
- **AND** adjusts border color for dark theme (rgba(255,255,255,0.08))

#### Scenario: Fallback for browsers without backdrop-filter support
- **WHEN** browser does not support backdrop-filter
- **THEN** system uses solid background color with higher opacity
- **AND** maintains visual consistency as much as possible
- **AND** uses @supports CSS feature detection

### Requirement: Use primary color #5C6BC0 throughout the interface

The system SHALL consistently use the primary indigo color #5C6BC0 for branding and interactive elements.

#### Scenario: Apply primary color to buttons
- **WHEN** system displays login button or logout button
- **THEN** button background uses #5C6BC0
- **AND** button text uses white color (#FFFFFF)
- **AND** button hover state uses darker shade (#3F51B5)
- **AND** button active/pressed state uses even darker shade (#303F9F)

#### Scenario: Apply primary color to status indicators
- **WHEN** system displays connection status indicator
- **THEN** connected state uses green color (not primary)
- **AND** disconnected state uses red color (not primary)
- **AND** connecting state uses primary color #5C6BC0

#### Scenario: Apply primary color to text highlights
- **WHEN** system displays system introduction or instructions
- **THEN** key words or phrases use #5C6BC0 color
- **AND** links use #5C6BC0 color
- **AND** focus states use #5C6BC0 outline color
