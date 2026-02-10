-- Create sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cookies TEXT NOT NULL,
    user_info TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- Create index on created_at for cleanup queries
CREATE INDEX IF NOT EXISTS idx_sessions_created_at ON sessions(created_at);
