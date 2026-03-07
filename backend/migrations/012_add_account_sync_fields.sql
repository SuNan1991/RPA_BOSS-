-- Migration 012: Add account sync fields
-- Date: 2026-03-06
-- Description: Add auto sync support fields for account management

-- 1. 添加同步相关字段
ALTER TABLE accounts ADD COLUMN auto_created BOOLEAN DEFAULT 0;
ALTER TABLE accounts ADD COLUMN last_sync_at TIMESTAMP;
ALTER TABLE accounts ADD COLUMN sync_source TEXT DEFAULT 'manual';
-- sync_source 可选值: 'manual', 'auto_login', 'import', 'auto_migration'

-- 2. 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_accounts_auto_created ON accounts(auto_created);
CREATE INDEX IF NOT EXISTS idx_accounts_sync_source ON accounts(sync_source);
CREATE INDEX IF NOT EXISTS idx_accounts_last_sync ON accounts(last_sync_at);

-- 3. 迁移现有数据（可选）
-- 将现有的 sessions 表中的数据同步到 accounts 表（如果还没有对应账号）
-- 注意：这里使用 INSERT OR IGNORE 避免重复

-- 先为现有 session 创建对应的账号记录（如果不存在）
INSERT OR IGNORE INTO accounts (phone, username, cookie_status, auto_created, sync_source, created_at, updated_at)
SELECT
    'auto_' || substr(hex(randomblob(4)), 1, 8) as phone,  -- 生成临时手机号，避免冲突
    CASE
        WHEN json_extract(user_info, '$.username') IS NOT NULL
        THEN json_extract(user_info, '$.username')
        ELSE 'BOSS用户'
    END as username,
    'valid' as cookie_status,
    1 as auto_created,
    'auto_migration' as sync_source,
    created_at,
    datetime('now') as updated_at
FROM sessions
WHERE user_info IS NOT NULL;

-- 4. 为自动创建的账号同步 session 数据到 account_sessions 表
INSERT OR REPLACE INTO account_sessions (account_id, cookies, user_info, created_at, expires_at, last_used_at)
SELECT
    a.id as account_id,
    s.cookies,
    s.user_info,
    s.created_at,
    s.expires_at,
    datetime('now') as last_used_at
FROM sessions s
JOIN accounts a ON (
    a.username = COALESCE(
        json_extract(s.user_info, '$.username'),
        'BOSS用户'
    )
    AND a.auto_created = 1
    AND a.sync_source = 'auto_migration'
)
WHERE s.user_info IS NOT NULL;
