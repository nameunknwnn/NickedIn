Create Table IF NOT EXISTS "USER"(
    id VARCHAR(255) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255),
    name VARCHAR (255),
    linkedin_access_token VARCHAR(255),
    linkedin_refresh_token VARCHAR(255),
    linkedin_token_expires_at TIMESTAMP
)