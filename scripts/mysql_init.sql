CREATE DATABASE IF NOT EXISTS shadownet;
USE shadownet;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE,
    password VARCHAR(50),
    bio TEXT
);

CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    content TEXT
);

CREATE TABLE IF NOT EXISTS internal_logs (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    event VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (username, password, bio) VALUES 
('admin', 'admin123', 'System overlord.'),
('guest', 'guest', 'Just a visitor.'),
('ceo', 'money123', 'I run the show.'),
('dev', 'coding_is_life', 'Working on the next big vuln.');

INSERT INTO internal_logs (event) VALUES 
('Login attempt for admin from 192.168.1.5'),
('SSRF attempt detected on /fetch'),
('New comment added to guestbook');

GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'root' WITH GRANT OPTION;
FLUSH PRIVILEGES;
