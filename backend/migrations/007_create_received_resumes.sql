-- 创建简历表
CREATE TABLE IF NOT EXISTS received_resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hr_job_id INTEGER NOT NULL,
    candidate_id INTEGER NOT NULL,
    resume_url TEXT,
    status TEXT DEFAULT 'pending',
    match_score REAL,
    notes TEXT,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hr_job_id) REFERENCES hr_jobs(id),
    FOREIGN KEY (candidate_id) REFERENCES candidates(id)
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_received_resumes_status ON received_resumes(status);
