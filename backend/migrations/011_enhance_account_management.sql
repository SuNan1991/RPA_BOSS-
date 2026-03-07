-- Migration 011: Enhance Account Management
-- Date: 2026-03-06
-- Description: Add tags, groups, notes, quota, and operation logs support

-- ============================================================================
-- 1. Enhance accounts table with new columns
-- ============================================================================

-- Add tags column (JSON format for flexibility)
ALTER TABLE accounts ADD COLUMN tags TEXT;

-- Add group_id for account grouping
ALTER TABLE accounts ADD COLUMN group_id INTEGER;

-- Add notes column for user remarks
ALTER TABLE accounts ADD COLUMN notes TEXT;

-- Add login_count to track login frequency
ALTER TABLE accounts ADD COLUMN login_count INTEGER DEFAULT 0;

-- Add last_operation_at to track activity
ALTER TABLE accounts ADD COLUMN last_operation_at TIMESTAMP;

-- Add quota_limit for daily operation limit
ALTER TABLE accounts ADD COLUMN quota_limit INTEGER DEFAULT 100;

-- Add quota_used to track today's usage
ALTER TABLE accounts ADD COLUMN quota_used INTEGER DEFAULT 0;

-- ============================================================================
-- 2. Create account_groups table for hierarchical grouping
-- ============================================================================

CREATE TABLE IF NOT EXISTS account_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    parent_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES account_groups(id) ON DELETE SET NULL
);

-- Index for parent_id lookups
CREATE INDEX IF NOT EXISTS idx_account_groups_parent ON account_groups(parent_id);

-- ============================================================================
-- 3. Create account_operation_logs table for activity tracking
-- ============================================================================

CREATE TABLE IF NOT EXISTS account_operation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL,
    operation_type TEXT NOT NULL,  -- login, logout, refresh_cookie, search, greet, etc.
    operation_detail TEXT,         -- JSON format for flexible data
    success BOOLEAN DEFAULT 1,
    error_message TEXT,
    duration_ms INTEGER,           -- Operation duration in milliseconds
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_operation_logs_account ON account_operation_logs(account_id);
CREATE INDEX IF NOT EXISTS idx_operation_logs_type ON account_operation_logs(operation_type);
CREATE INDEX IF NOT EXISTS idx_operation_logs_created ON account_operation_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_operation_logs_success ON account_operation_logs(success);

-- ============================================================================
-- 4. Create indexes for accounts table
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_accounts_group ON accounts(group_id);
CREATE INDEX IF NOT EXISTS idx_accounts_cookie_status ON accounts(cookie_status);
CREATE INDEX IF NOT EXISTS idx_accounts_is_active ON accounts(is_active);

-- ============================================================================
-- 5. Create trigger to update updated_at timestamp
-- ============================================================================

CREATE TRIGGER IF NOT EXISTS update_account_groups_timestamp
    AFTER UPDATE ON account_groups
    FOR EACH ROW
BEGIN
    UPDATE account_groups SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
