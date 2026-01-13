# ShadowNet: Monolithic Pentest Lab

![ShadowNet](https://img.shields.io/badge/ShadowNet-Pentest%20Lab-red?style=for-the-badge)

Welcome to **ShadowNet**, a comprehensive single-machine penetration testing laboratory. ShadowNet is designed to simulate a realistic target environment where multiple services and vulnerabilities coexist on a single host.

## 🚀 Getting Started

Ensure you have [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) installed.

1.  **Clone/Download** this repository.
2.  **Navigate** to the `shadownet` directory.
3.  **Launch the lab:**
    ```bash
    docker-compose up --build -d
    ```

## 🎯 Lab Target Overview

ShadowNet runs on a single monolithic container with the following services exposed:

| Service | Port | Description |
| :--- | :--- | :--- |
| **Apache Gateway** | 80 | External gateway vulnerable to **Shellshock (CVE-2014-6271)**. |
| **ShadowWork Suite** | 8080 | Productivity Suite with Task Manager, Expense Vault, and Integrations. |

> [!WARNING]
> **MacOS Users:** Port 5000 is often used by **AirPlay Receiver (AirTunes)**. 
> The Flask application is mapped to **Port 8080** internally and externally in this lab to avoid this conflict. 
> If you see a `403 Forbidden` from `AirTunes` on port 5000, use `http://localhost:8080`.
| **FTP** | 21 | Exposed with `anonymous` access enabled. |
| **SSH** | 2222 | Weak credentials (`service:password`). |
| **MySQL** | 3306 | Standard port, weak credentials (`root:root`). |
| **Redis** | 6379 | No authentication required. |
| **LDAP** | 389 | Anonymous Bind enabled. |

---

## 🛠 Vulnerabilities Guide

### 1. Shadow-Flask (Port 5000)
Explore the following flaws in the main web application:
- **SQL Injection:** Bypass the login page using classic tautologies like `' OR 1=1 --`.
- **Stored XSS:** Leave a script in the guestbook to trigger when others view it.
- **IDOR:** Access `/profile/<id>` to view sensitive info of other users without authorization.
- **Command Injection (RCE):** Use the "Network Diagnostic Unit" (Ping) to execute OS commands (e.g., `; id`).
- **SSRF:** Use the "URL Fetcher" to probe internal services like `http://localhost:6379` (Redis).
- **SSTI:** Manipulate the `/greet?name=` parameter with Jinja2 syntax like `{{ 7*7 }}`.

### 2. Shellshock (Port 80)
The legacy CGI script at `/cgi-bin/vulnerable.cgi` is vulnerable to Shellshock.
- **Payload Example:**
  ```bash
  curl -H "User-Agent: () { :; }; echo; /usr/bin/id" http://<IP>/cgi-bin/vulnerable.cgi
  ```

### 3. Infrastructure Flaws
- **FTP:** Connect with user `anonymous` and any password.
- **SSH:** Connect with `ssh service@<IP> -p 2222` using password `password`.
- **MySQL:** Connect with `mysql -h <IP> -P 3306 -u root -proot`.
- **Redis:** Use `redis-cli -h <IP>` with no password.
- **LDAP:** Use `ldapsearch -x -H ldap://<IP>:389 -b "dc=example,dc=org"` (Anonymous Bind).

---

## 🔒 Security Disclaimer
This lab is for **educational purposes only**. It is intentionally highly vulnerable and should **never** be exposed to a public network. Always run it in a controlled, isolated environment.

---
**ShadowNet** - *Master the Shadows.*
