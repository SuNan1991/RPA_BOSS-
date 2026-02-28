-- 创建HR职位表
CREATE TABLE IF NOT EXISTS hr_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hr_account_id INTEGER NOT NULL,
    job_name TEXT NOT NULL,
    department TEXT,
    salary_range TEXT,
    experience_requirement TEXT,
    education_requirement TEXT,
    description TEXT,
    requirements TEXT,
    benefits TEXT,
    status TEXT DEFAULT 'active',
    boss_job_id TEXT,
    refresh_count INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
    applicant_count INTEGER DEFAULT 0,
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hr_account_id) REFERENCES accounts(id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_hr_jobs_status ON hr_jobs(status);
CREATE INDEX IF NOT EXISTS idx_hr_jobs_hr_account ON hr_jobs(hr_account_id);
