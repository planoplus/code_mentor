CREATE TABLE developers (
    id SERIAL PRIMARY KEY,
    author_hkey TEXT UNIQUE,
    display_name TEXT
);

CREATE TABLE commits (
    id SERIAL PRIMARY KEY,
    commit_sha TEXT UNIQUE,
    repo TEXT,
    author_hkey TEXT,
    committed_at TIMESTAMP,
    files_changed INT,
    loc_add INT,
    loc_del INT
);

CREATE TABLE scores (
    id SERIAL PRIMARY KEY,
    commit_sha TEXT REFERENCES commits(commit_sha),
    repo TEXT,
    author_hkey TEXT,
    sqc NUMERIC,
    subnotes JSONB,
    rationale TEXT,
    created_at TIMESTAMP DEFAULT now(),
    CONSTRAINT unique_commit_sha UNIQUE (commit_sha)
);