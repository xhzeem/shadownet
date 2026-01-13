# ShadowNet Monolithic Lab Walkthrough

ShadowNet is a consolidated pentest lab contained within a single machine (Docker container). It features a wide array of vulnerabilities and misconfigurations across multiple services.

## Services & Vulnerabilities Verified

### 1. Web Applications
- **ShadowCorp Internal Portal (Port 8080):**
  - **Auth System (SQLi):** Verified bypass on `/login`.
  - **CorpFeed (XSS):** Verified stored script reflection on `/feed`.
  - **Personnel Directory (IDOR):** Verified unauthorized access to profiles on `/directory/<id>`.
  - **NetTools (RCE/SSRF):** Verified command injection and service probing on `/tools`.
  - **Account Settings (SSTI):** Verified template injection via personalization engine on `/settings`.
- **Apache Gateway (Port 80):**
  - **Shellshock RCE:** Verified! Supports standard paths like `/cgi-bin/test.cgi` and `/cgi-bin/status.cgi`.


### 3. Data & Environment Population
- **MySQL:** Populated with `internal_logs` and multiple user roles (`ceo`, `dev`).
- **Redis:** Populated with mock sessions and the `SECRET_ADMIN_TOKEN` flag.
- **LDAP:** Populated with "ShadowCorp" directory structure and employee uids.
- **FTP:** Added `config.bak` and a `flag.txt` to the public directory.
- **SSH:** Populated `service` home directory with `notes.txt` and `.bash_history`.

## Exploit Scripts
A suite of Python scripts has been provided in the `shadownet/exploits/` directory to automate the verification of each vulnerability. These include:
- `sqli_exploit.py`: Bypasses login.
- `xss_exploit.py`: Injects and verifies stored XSS.
- `idor_exploit.py`: Enumerates user profiles.
- `rce_exploit.py`: Obtains OS command execution.
- `ssrf_exploit.py`: Probes internal services.
- `ssti_exploit.py`: Leaks server configuration.
- `shellshock_exploit.py`: Verified RCE on Apache.
- `infra_tests.py`: Tests FTP, SSH, MySQL, Redis, and LDAP.


## Implementation Details
- **Architecture:** Monolithic container built on `debian:bullseye-slim`.
- **Process Management:** `supervisord` manages all 7 services.
- **Vulnerability Injection:** 
  - Manually installed vulnerable `bash 4.3` for Shellshock.
  - Flask app uses raw string interpolation and `subprocess.check_output(shell=True)`.
  - Infrastructure configs stripped of authentication/security headers.

## Documentation
- A comprehensive [README.md](file:///Users/xhzeem/Desktop/lab333/shadownet/README.md) is included with exploitation guides for each vulnerability.
