-- Create login_logs table
CREATE TABLE IF NOT EXISTS login_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    success BOOLEAN NOT NULL DEFAULT 0,
    failure_reason TEXT,
    ip_address TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on timestamp for querying recent logs
CREATE INDEX IF NOT EXISTS idx_login_logs_timestamp ON login_logs(timestamp DESC);
