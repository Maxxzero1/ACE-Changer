-- filename: database_schema.sql
-- This schema is for the main data storage of the bot:
-- It manages users (owners, admins, users), groups/channels, their roles, ban lists, and bot membership info.

-- Table to store Owners info
CREATE TABLE owners (
    owner_id BIGINT PRIMARY KEY,  -- Telegram user ID
    owner_name VARCHAR(100) NOT NULL
);

-- Table to store Groups or Channels where bot is member
CREATE TABLE chat_groups (
    chat_id BIGINT PRIMARY KEY,     -- Channel or Group ID
    chat_title VARCHAR(255),
    chat_type VARCHAR(20) CHECK (chat_type IN ('group', 'supergroup', 'channel')) NOT NULL
);

-- Table to store Admins per chat group/channel
CREATE TABLE admins (
    chat_id BIGINT REFERENCES chat_groups(chat_id) ON DELETE CASCADE,
    admin_id BIGINT,                -- Telegram user ID
    PRIMARY KEY (chat_id, admin_id)
);

-- Table to store regular Users per chat group/channel
CREATE TABLE users (
    chat_id BIGINT REFERENCES chat_groups(chat_id) ON DELETE CASCADE,
    user_id BIGINT,
    PRIMARY KEY (chat_id, user_id)
);

-- Table to store ban list for users, owners can ban/unban users globally or per chat
CREATE TABLE banned_users (
    user_id BIGINT PRIMARY KEY,
    banned_by_owner_id BIGINT REFERENCES owners(owner_id),
    ban_reason TEXT,
    banned_at TIMESTAMP DEFAULT NOW()
);

-- Table to store per-chat settings, like who can request prices, announcement intervals, etc.
CREATE TABLE chat_settings (
    chat_id BIGINT PRIMARY KEY REFERENCES chat_groups(chat_id) ON DELETE CASCADE,
    allow_price_requests BOOLEAN DEFAULT FALSE,
    price_announcement_interval_minutes INTEGER DEFAULT 60 CHECK (price_announcement_interval_minutes BETWEEN 1 AND 1440)
);

-- Table to track which chats bot is currently member of, and when added
CREATE TABLE bot_memberships (
    chat_id BIGINT PRIMARY KEY REFERENCES chat_groups(chat_id) ON DELETE CASCADE,
    joined_at TIMESTAMP DEFAULT NOW()
);