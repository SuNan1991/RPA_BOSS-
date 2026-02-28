-- 创建自动回复规则表
CREATE TABLE IF NOT EXISTS auto_reply_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hr_account_id INTEGER NOT NULL,
    trigger_keywords TEXT NOT NULL,
    reply_template TEXT NOT NULL,
    auto_invite BOOLEAN DEFAULT 0,
    priority INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hr_account_id) REFERENCES accounts(id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_auto_reply_rules_hr_account ON auto_reply_rules(hr_account_id);
CREATE INDEX IF NOT EXISTS idx_auto_reply_rules_active ON auto_reply_rules(is_active);
