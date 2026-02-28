-- 创建沟通记录表
CREATE TABLE IF NOT EXISTS communications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER NOT NULL,
    hr_account_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    content TEXT,
    direction TEXT,
    status TEXT DEFAULT 'sent',
    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES candidates(id),
    FOREIGN KEY (hr_account_id) REFERENCES accounts(id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_communications_candidate ON communications(candidate_id);
CREATE INDEX IF NOT EXISTS idx_communications_hr_account ON communications(hr_account_id);
