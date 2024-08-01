DROP DATABASE IF EXISTS huskerlyinvitesdb;

CREATE DATABASE huskerlyinvitesdb;

USE huskerlyinvitesdb;

CREATE TABLE organization_invites (
    user_email VARCHAR(255) UNIQUE NOT NULL,
    org_id BIGINT UNSIGNED NOT NULL,
    created_by_email VARCHAR(255) NOT NULL,
    created_date TIMESTAMP DEFAULT NOW(),
    expiration_date TIMESTAMP,
    active BOOLEAN DEFAULT TRUE NOT NULL,
    PRIMARY KEY (user_email, org_id)
);

CREATE TABLE organization_requests (
    org_name VARCHAR(255) NOT NULL,
    created_by_email VARCHAR(255) UNIQUE NOT NULL,
    created_date TIMESTAMP DEFAULT NOW(),
    status ENUM ('PENDING', 'APPROVED', 'REJECTED') DEFAULT 'PENDING' NOT NULL,
    -- TODO: add column for admin_email to track who approved/rejected
    PRIMARY KEY (org_name, created_by_email)
);