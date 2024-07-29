-- CREATE DATABASE huskerlyinvites;

CREATE TABLE IF NOT EXISTS organization_invites (
    user_email TEXT,
    org_id INT,
    created_by_email TEXT NOT NULL,
    created_date TIMESTAMP DEFAULT NOW(),
    expiration_date TIMESTAMP DEFAULT NOW() + INTERVAL '1 week',
    active BOOLEAN DEFAULT TRUE NOT NULL,
    PRIMARY KEY (user_email, org_id)
);

-- CREATE TYPE org_request_status AS ENUM ('PENDING', 'APPROVED', 'REJECTED');

CREATE TABLE organization_requests (
    org_name TEXT NOT NULL,
    created_by_email TEXT NOT NULL,
    created_date TIMESTAMP DEFAULT NOW(),
    status org_request_status DEFAULT 'PENDING' NOT NULL,
    PRIMARY KEY (org_name, created_by_email)
);

-- CREATE TABLE organization_lost_privileges (
--     org_id INT,
--     user_email TEXT UNIQUE NOT NULL,
--     lost_date TIMESTAMP DEFAULT NOW(),
--     active BOOLEAN NOT NULL,
--     PRIMARY KEY (org_id, user_email)
-- --     FOREIGN KEY (org_id) REFERENCES organizations(id)
-- );