CREATE DATABASE IF NOT EXISTS shadownet;
USE shadownet;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(50),
    bio TEXT,
    role VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    content TEXT,
    author VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS internal_logs (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    event VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (username, password, bio, role) VALUES 
('admin', 'admin123', 'Chief Security Officer at ShadowCorp. Overseeing all internal systems.', 'CSO'),
('j.doe', 'secret123', 'Senior Backend Engineer. Working on internal API integrations.', 'Developer'),
('b.wayne', 'nananana', 'Board of Directors. Focused on global expansion.', 'Executive'),
('s.connors', 'password', 'HR Manager. Handling personnel directory and employee relations.', 'HR'),
('m.ross', 'specter7', 'Lead Architect. Responsible for the monolithic evolution.', 'Architect'),
('ceo', 'money123', 'Managing business operations and stakeholder relations.', 'CEO');

INSERT INTO comments (content, author) VALUES 
('Welcome everyone to the new ShadowCorp portal! Stay secure.', 'admin'),
('Network tools migrating to v2.0 next week. Expect some downtime.', 'j.doe'),
('Please update your profile bio by EOD tomorrow.', 's.connors');

INSERT INTO internal_logs (event) VALUES 
('System heartbeat check - OK'),
('Remote resource sync initiated'),
('New entry in public message board'),
('Log rotation performed successfully');

GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'root' WITH GRANT OPTION;
FLUSH PRIVILEGES;
