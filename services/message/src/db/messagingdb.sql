DROP DATABASE IF EXISTS huskerlymessagingdb;

CREATE DATABASE huskerlymessagingdb;

USE huskerlymessagingdb;

CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    deleted BOOLEAN DEFAULT FALSE NOT NULL,
    created_date TIMESTAMP DEFAULT NOW(),
    created_by_email VARCHAR(255) NOT NULL
);

CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    org_id BIGINT UNSIGNED NOT NULL,
    created_date TIMESTAMP DEFAULT NOW(),
    created_by_email VARCHAR(255) NOT NULL,
    deleted BOOLEAN DEFAULT FALSE NOT NULL,
    FOREIGN KEY (org_id) REFERENCES organizations(id)
);

CREATE TABLE chats (
    id SERIAL PRIMARY KEY,
    chat_type ENUM('STREAM', 'DIRECT_MESSAGE') NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_date TIMESTAMP DEFAULT NOW(),
    created_by_email VARCHAR(255) NOT NULL,
    deleted BOOLEAN DEFAULT FALSE NOT NULL,
    public BOOLEAN NOT NULL,
    team_id BIGINT UNSIGNED,
    org_id BIGINT UNSIGNED,
    FOREIGN KEY (team_id) REFERENCES teams(id),
    FOREIGN KEY (org_id) REFERENCES organizations(id),
    CHECK (
        (chat_type = 'STREAM' AND team_id IS NOT NULL AND org_id IS NULL) OR
        (chat_type = 'DIRECT_MESSAGE' AND org_id IS NOT NULL AND team_id IS NULL)
    )
);

CREATE TABLE team_users (
    user_email VARCHAR(255),
    team_id BIGINT UNSIGNED,
    joined_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_email, team_id),
    FOREIGN KEY (team_id) REFERENCES teams(id)
);

CREATE TABLE chat_users (
    user_email VARCHAR(255),
    chat_id BIGINT UNSIGNED,
    joined_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_email, chat_id),
    FOREIGN KEY (chat_id) REFERENCES chats(id)
);

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_email VARCHAR(255) NOT NULL,
    parent_post_id BIGINT UNSIGNED,
    chat_id BIGINT UNSIGNED NOT NULL,
    content VARCHAR(255) NOT NULL,
    created_date TIMESTAMP DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE NOT NULL,
    edited_at TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES chats(id),
    FOREIGN KEY (parent_post_id) REFERENCES posts(id) ON DELETE SET NULL
);

CREATE TABLE reaction_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE team_icons (
    team_id BIGINT UNSIGNED,
    url VARCHAR(255) UNIQUE NOT NULL,
    created_date TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (team_id) REFERENCES teams(id)
);

CREATE TABLE post_reactions (
    post_id SERIAL,
    user_email VARCHAR(255) NOT NULL,
    reaction_id BIGINT UNSIGNED NOT NULL,
    created_date TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (post_id, user_email),
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (reaction_id) REFERENCES reaction_types(id)
);

CREATE TABLE attachments (
    id SERIAL PRIMARY KEY,
    post_id BIGINT UNSIGNED NOT NULL,
    url VARCHAR(255) NOT NULL,
    created_date TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

