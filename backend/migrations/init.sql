CREATE TABLE IF NOT EXISTS "USER"(
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255),
    name VARCHAR(255),
    linkedin_access_token TEXT,
    linkedin_refresh_token TEXT,
    linkedin_token_expires_at INTEGER
);

ALTER TABLE "USER" ALTER COLUMN linkedin_access_token TYPE TEXT;
ALTER TABLE "USER" ALTER COLUMN linkedin_refresh_token TYPE TEXT;
ALTER TABLE "USER" ALTER COLUMN email DROP NOT NULL;