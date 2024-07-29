-- CREATE DATABASE huskerlydatabase;

CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    active BOOLEAN DEFAULT TRUE NOT NULL,
    created_date TIMESTAMP DEFAULT NOW(),
    created_by_email TEXT NOT NULL,
    lead_admin_email TEXT UNIQUE NOT NULL
);

CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    name TEXT,
    created_date TIMESTAMP DEFAULT NOW()
);

CREATE TABLE chat_types (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE chats (
    id SERIAL PRIMARY KEY,
    chat_type_id INT NOT NULL,
    name TEXT,
    created_date TIMESTAMP DEFAULT NOW(),
--     public BOOLEAN NOT NULL,
    FOREIGN KEY (chat_type_id) REFERENCES chat_types(id)
);

CREATE TABLE streams (
    team_id INT,
    public BOOLEAN NOT NULL,
    FOREIGN KEY (team_id) REFERENCES teams(id)
) INHERITS (chats);

CREATE TABLE direct_messages (
    org_id INT,
    FOREIGN KEY (org_id) REFERENCES organizations(id)
) INHERITS (chats);

CREATE TABLE team_users (
    user_email TEXT,
    team_id INT,
    joined_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_email, team_id),
    FOREIGN KEY (team_id) REFERENCES teams(id)
);

CREATE TABLE chat_users (
    user_email TEXT,
    chat_id INT,
    joined_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (user_email, chat_id),
    FOREIGN KEY (chat_id) REFERENCES chats(id)
);

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    user_email TEXT NOT NULL,
    parent_post_id INT,
    chat_id INT NOT NULL,
    content TEXT,
    created_date TIMESTAMP DEFAULT NOW(),
    visible BOOLEAN DEFAULT TRUE,
    edited_at TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES chats(id)
);

CREATE TABLE reaction_types (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE team_icons (
    team_id INT,
    url TEXT UNIQUE NOT NULL,
    created_date TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (team_id) REFERENCES teams(id)
);

CREATE TABLE post_reactions (
    post_id INT,
    user_email TEXT,
    reaction_id INT NOT NULL,
    created_date TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (post_id, user_email),
    FOREIGN KEY (post_id) REFERENCES posts(id),
    FOREIGN KEY (reaction_id) REFERENCES reaction_types(id)
);

CREATE TABLE attachments (
    id SERIAL PRIMARY KEY,
    post_id INT,
    url TEXT UNIQUE NOT NULL,
    created_date TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

