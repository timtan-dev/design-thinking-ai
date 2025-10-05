-- Design Thinking AI Agent - Database Initialization
-- SQLite/PostgreSQL compatible schema

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    area VARCHAR(255) NOT NULL,
    goal TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(255)
);

-- Stage progress tracking
CREATE TABLE IF NOT EXISTS stage_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    stage_number INTEGER NOT NULL,
    status VARCHAR(50) DEFAULT 'not_started',
    data TEXT,  -- JSON stored as text
    completed_at TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Research data
CREATE TABLE IF NOT EXISTS research_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    method_type VARCHAR(100) NOT NULL,
    file_path VARCHAR(500),
    processed_data TEXT,  -- JSON stored as text
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Generated content
CREATE TABLE IF NOT EXISTS generated_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    stage VARCHAR(50) NOT NULL,
    content_type VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT,  -- JSON stored as text
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Templates
CREATE TABLE IF NOT EXISTS templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    method_type VARCHAR(100) NOT NULL UNIQUE,
    template_content TEXT NOT NULL,
    version VARCHAR(20) DEFAULT '1.0',
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_projects_user_id ON projects(user_id);
CREATE INDEX IF NOT EXISTS idx_stage_progress_project_id ON stage_progress(project_id);
CREATE INDEX IF NOT EXISTS idx_research_data_project_id ON research_data(project_id);
CREATE INDEX IF NOT EXISTS idx_generated_content_project_id ON generated_content(project_id);
CREATE INDEX IF NOT EXISTS idx_generated_content_stage ON generated_content(stage);
