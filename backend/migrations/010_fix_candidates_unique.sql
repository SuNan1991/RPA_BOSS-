-- 修复候选人表的唯一约束
-- 问题: profile_url 的 UNIQUE 约束阻止同一候选人被不同 HR 账户记录
-- 解决: 改为 (hr_account_id, profile_url) 复合唯一约束

-- 由于 SQLite 不支持直接修改约束，需要重建表

-- 1. 创建新的候选人表
CREATE TABLE IF NOT EXISTS candidates_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    position TEXT,
    experience TEXT,
    education TEXT,
    expected_salary TEXT,
    recent_company TEXT,
    skills TEXT,
    profile_url TEXT,
    status TEXT DEFAULT 'active',
    hr_account_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hr_account_id) REFERENCES accounts(id),
    UNIQUE(hr_account_id, profile_url)
);

-- 2. 迁移现有数据
INSERT INTO candidates_new (id, name, position, experience, education, expected_salary, recent_company, skills, profile_url, status, hr_account_id, created_at, updated_at)
SELECT id, name, position, experience, education, expected_salary, recent_company, skills, profile_url, status, hr_account_id, created_at, updated_at
FROM candidates;

-- 3. 删除旧表
DROP TABLE candidates;

-- 4. 重命名新表
ALTER TABLE candidates_new RENAME TO candidates;

-- 5. 重建索引
CREATE INDEX IF NOT EXISTS idx_candidates_status ON candidates(status);
CREATE INDEX IF NOT EXISTS idx_candidates_hr_account ON candidates(hr_account_id);
CREATE INDEX IF NOT EXISTS idx_candidates_profile_url ON candidates(profile_url);
