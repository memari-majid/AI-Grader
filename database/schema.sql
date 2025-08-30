-- CS AI Grader Database Schema
-- Secure storage for users, assignments, and grading data

-- Users table for authentication and role management
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('professor', 'ta', 'admin')),
    department TEXT DEFAULT 'Computer Science',
    courses TEXT, -- JSON array of course codes
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    api_usage_count INTEGER DEFAULT 0,
    api_usage_reset_date DATE DEFAULT CURRENT_DATE
);

-- Sessions table for secure session management
CREATE TABLE IF NOT EXISTS user_sessions (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    ip_address TEXT,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Assignments table for storing assignment metadata
CREATE TABLE IF NOT EXISTS assignments (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    course_code TEXT NOT NULL,
    prompt TEXT,
    rubric_json TEXT, -- JSON rubric data
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    assignment_type TEXT DEFAULT 'programming',
    learning_objectives TEXT, -- JSON array
    FOREIGN KEY (created_by) REFERENCES users (id)
);

-- Student submissions and grading results
CREATE TABLE IF NOT EXISTS grading_sessions (
    id TEXT PRIMARY KEY,
    assignment_id TEXT NOT NULL,
    grader_id INTEGER NOT NULL,
    student_identifier_hash TEXT, -- Hashed for privacy
    student_code TEXT,
    code_metrics_json TEXT, -- Static analysis results
    ai_scores_json TEXT, -- AI-generated scores
    ai_feedback_json TEXT, -- AI-generated feedback
    final_scores_json TEXT, -- Final scores after TA review
    final_feedback_json TEXT, -- Final feedback after TA review
    total_score INTEGER,
    percentage REAL,
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'completed', 'flagged')),
    time_started TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    time_completed TIMESTAMP,
    grading_duration_seconds INTEGER,
    edit_count INTEGER DEFAULT 0, -- Number of edits made to AI suggestions
    ai_acceptance_rate REAL, -- Percentage of AI suggestions accepted
    research_consent BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (assignment_id) REFERENCES assignments (id),
    FOREIGN KEY (grader_id) REFERENCES users (id)
);

-- Knowledge base for storing common feedback patterns and improvements
CREATE TABLE IF NOT EXISTS knowledge_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL, -- 'feedback_template', 'common_issue', 'improvement_suggestion'
    topic TEXT NOT NULL, -- 'functions', 'loops', 'style', etc.
    content TEXT NOT NULL,
    usage_count INTEGER DEFAULT 0,
    effectiveness_rating REAL, -- Based on user feedback
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (created_by) REFERENCES users (id)
);

-- Audit log for security and research tracking
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    session_id TEXT,
    action TEXT NOT NULL, -- 'login', 'grade_assignment', 'generate_feedback', etc.
    resource_type TEXT, -- 'assignment', 'grading_session', 'knowledge_base'
    resource_id TEXT,
    details_json TEXT, -- Additional context
    ip_address TEXT,
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (session_id) REFERENCES user_sessions (id)
);

-- User feedback for app improvement
CREATE TABLE IF NOT EXISTS user_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    feedback_type TEXT NOT NULL, -- 'bug', 'feature_request', 'improvement', 'rating'
    message TEXT NOT NULL,
    rating INTEGER CHECK (rating BETWEEN 1 AND 5),
    context_json TEXT, -- Current app state when feedback given
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'open' CHECK (status IN ('open', 'reviewed', 'implemented', 'closed')),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Research data aggregation for analytics
CREATE TABLE IF NOT EXISTS research_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_type TEXT NOT NULL, -- 'grading_efficiency', 'ai_accuracy', 'user_satisfaction'
    metric_value REAL NOT NULL,
    context_json TEXT,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    period_start DATE,
    period_end DATE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires ON user_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_grading_assignment ON grading_sessions(assignment_id);
CREATE INDEX IF NOT EXISTS idx_grading_grader ON grading_sessions(grader_id);
CREATE INDEX IF NOT EXISTS idx_grading_student ON grading_sessions(student_identifier_hash);
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge_base(category, topic);
