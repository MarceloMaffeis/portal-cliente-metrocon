
-- Schema do Portal do Cliente Metrocon Engenharia

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'engineer', 'client')),
    phone TEXT,
    company TEXT,
    active INTEGER DEFAULT 1,
    lgpd_consent_date TEXT,
    created_at TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('obra', 'reforma', 'administrativo')),
    category_label TEXT NOT NULL,
    description TEXT,
    address_or_agency TEXT,
    protocol_number TEXT,
    status TEXT NOT NULL CHECK(status IN ('planejamento', 'em_andamento', 'em_aprovacao_orgao', 'concluido', 'pausado')),
    progress_percent REAL DEFAULT 0.0,
    start_date TEXT,
    end_date_estimated TEXT,
    responsible_name TEXT,
    responsible_phone TEXT,
    responsible_email TEXT,
    technical_notes TEXT,
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY(client_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL CHECK(category IN ('projetos', 'contratos', 'documentos_legais', 'aprovacoes', 'anexos')),
    title TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size_kb REAL DEFAULT 0.0,
    version TEXT DEFAULT '1.0',
    is_current INTEGER DEFAULT 1,
    notes TEXT,
    uploaded_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY(project_id) REFERENCES projects(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS daily_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    log_date TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    weather_conditions TEXT,
    team_count INTEGER DEFAULT 0,
    highlight_activities TEXT,
    occurrences TEXT,
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY(project_id) REFERENCES projects(id),
    FOREIGN KEY(author_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS daily_log_photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    daily_log_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    file_name TEXT NOT NULL,
    caption TEXT,
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY(daily_log_id) REFERENCES daily_logs(id)
);

CREATE TABLE IF NOT EXISTS schedule_stages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    stage_name TEXT NOT NULL,
    stage_type TEXT NOT NULL CHECK(stage_type IN ('execucao', 'orgao_publico', 'documental', 'vistoria')),
    description TEXT,
    agency_name TEXT,
    protocol_number TEXT,
    start_date TEXT,
    end_date TEXT,
    progress_percent REAL DEFAULT 0.0,
    status TEXT NOT NULL CHECK(status IN ('a_iniciar', 'em_andamento', 'em_analise_orgao', 'concluido', 'atrasado')),
    order_index INTEGER DEFAULT 0,
    FOREIGN KEY(project_id) REFERENCES projects(id)
);

CREATE TABLE IF NOT EXISTS meeting_minutes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    meeting_date TEXT NOT NULL,
    location_or_link TEXT,
    participants TEXT,
    summary_topics TEXT,
    decisions TEXT,
    action_items TEXT,
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY(project_id) REFERENCES projects(id)
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    sender_id INTEGER NOT NULL,
    recipient_id INTEGER,
    subject TEXT NOT NULL,
    content TEXT NOT NULL,
    attachment_path TEXT,
    attachment_name TEXT,
    is_read INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now', 'localtime')),
    FOREIGN KEY(project_id) REFERENCES projects(id),
    FOREIGN KEY(sender_id) REFERENCES users(id),
    FOREIGN KEY(recipient_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    user_name TEXT,
    user_role TEXT,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT,
    details TEXT,
    ip_or_session TEXT,
    timestamp TEXT DEFAULT (datetime('now', 'localtime'))
);

CREATE INDEX IF NOT EXISTS idx_projects_client ON projects(client_id);
CREATE INDEX IF NOT EXISTS idx_docs_project ON documents(project_id);
CREATE INDEX IF NOT EXISTS idx_logs_project ON daily_logs(project_id);
CREATE INDEX IF NOT EXISTS idx_stages_project ON schedule_stages(project_id);
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id);
