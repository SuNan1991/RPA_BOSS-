-- 创建候选人表
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    position TEXT,
    experience TEXT,
    education TEXT,
    expected_salary TEXT,
    recent_company TEXT,
    skills TEXT,
    profile_url TEXT UNIQUE,
    status TEXT DEFAULT 'active',
    hr_account_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hr_account_id) REFERENCES accounts(id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_candidates_status ON candidates(status);
CREATE INDEX IF NOT EXISTS idx_candidates_hr_account ON candidates(hr_account_id);
