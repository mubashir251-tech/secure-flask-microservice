# 🔐 Secure Flask Microservice Platform

> **Production-style containerized Flask + PostgreSQL microservice deployed with Podman, with security hardening, secret management, persistent storage, health checks, resource controls, vulnerability scanning, observability, and recovery testing.**

[![Python](https://img.shields.io/badge/Python-3.9-blue?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-API-black?logo=flask)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15%2B-blue?logo=postgresql)](https://www.postgresql.org/)
[![Podman](https://img.shields.io/badge/Container-Podman-purple?logo=podman)](https://podman.io/)
[![Security](https://img.shields.io/badge/Security-Trivy-red?logo=aquasecurity)](https://trivy.dev/)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-black?logo=githubactions)](https://github.com/features/actions)

---

## 📌 Project Overview

This project demonstrates how to design, secure, deploy, troubleshoot, and operate a **multi-container Flask microservice** backed by PostgreSQL.

The project is intentionally designed around a realistic business scenario rather than a simple container tutorial.

### 🎯 Business Scenario

A small business needs a backend API that must:

- Run reliably in containers
- Store application data persistently
- Protect database credentials
- Prevent unnecessary root access
- Detect vulnerable container dependencies
- Wait for PostgreSQL to become ready
- Recover from database interruptions
- Control CPU and memory consumption
- Provide useful logs for troubleshooting
- Be reproducible through infrastructure configuration

---

# 🏗️ Architecture

```text
                              ┌──────────────────┐
                              │      Client      │
                              │ Browser / curl    │
                              └────────┬─────────┘
                                       │
                                       │ HTTP
                                       ▼
                              ┌──────────────────┐
                              │      NGINX       │
                              │ Reverse Proxy    │
                              └────────┬─────────┘
                                       │
                                       │ HTTP :5000
                                       ▼
                     ┌────────────────────────────────┐
                     │          Flask API              │
                     │                                │
                     │  • Non-root execution          │
                     │  • Health checks               │
                     │  • Environment configuration   │
                     │  • Secret-file support         │
                     │  • Database connection         │
                     └──────────────┬─────────────────┘
                                    │
                                    │ PostgreSQL
                                    │ private network
                                    ▼
                     ┌────────────────────────────────┐
                     │          PostgreSQL             │
                     │                                │
                     │  • Healthcheck                 │
                     │  • Secret password             │
                     │  • Persistent storage           │
                     └──────────────┬─────────────────┘
                                    │
                                    ▼
                           ┌─────────────────┐
                           │ Persistent      │
                           │ Podman Volume   │
                           └─────────────────┘
```

---

# 🔒 Security Architecture

```text
                         Source Code
                              │
                              ▼
                       Container Build
                              │
                              ▼
                    ┌──────────────────┐
                    │ Vulnerability    │
                    │ Scan — Trivy     │
                    └────────┬─────────┘
                             │
                    ┌────────┴─────────┐
                    │                  │
                 FAIL               PASS
                    │                  │
                    ▼                  ▼
                  STOP            Application
                                   Testing
                                      │
                                      ▼
                               Image Release
                                      │
                                      ▼
                                  Deployment
```

### Security controls implemented

| Control | Implementation |
|---|---|
| Least privilege | Flask runs as non-root |
| Secret management | Podman secrets |
| Credential protection | No passwords committed to Git |
| Image security | Trivy vulnerability scanning |
| Minimal image | Python slim base image |
| Network isolation | Private application network |
| Resource protection | CPU / memory limits |
| Persistence | PostgreSQL named volume |
| Service readiness | PostgreSQL healthcheck |
| Failure handling | Application retry logic |
| Logging | Podman container logs |
| Recovery testing | Database restart testing |

---

# 🧰 Technology Stack

| Layer | Technology |
|---|---|
| Application | Python 3.9 / Flask |
| Database | PostgreSQL |
| Container Runtime | Podman |
| Multi-container Deployment | Podman Compose |
| Container Networking | Podman bridge network |
| Persistence | Podman named volume |
| Secrets | Podman Secrets |
| Vulnerability Scanner | Trivy |
| Testing | pytest / curl |
| CI/CD | GitHub Actions |
| Host OS | Ubuntu Linux |

---

# 📁 Repository Structure

```text
secure-flask-microservice/
│
├── app/
│   ├── app.py
│   └── requirements.txt
│
├── database/
│   └── init.sql
│
├── container/
│   ├── Containerfile
│   └── entrypoint.sh
│
├── compose/
│   └── podman-compose.yml
│
├── security/
│   └── README.md
│
├── tests/
│   └── README.md
│
├── scripts/
│   └── README.md
│
├── docs/
│   ├── architecture.md
│   ├── deployment.md
│   └── troubleshooting.md
│
├── screenshots/
│   └── deployment-evidence/
│
├── .github/
│   └── workflows/
│
├── .gitignore
└── README.md
```

---

# 🚀 Application Features

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Application status |
| `/health` | GET | Health/readiness check |
| `/data` | GET | PostgreSQL connectivity test |

### Example

```bash
curl http://localhost:5000/
```

Expected response:

```json
{
  "status": "OK",
  "message": "Flask Microservice Running"
}
```

Database connectivity:

```bash
curl http://localhost:5000/data
```

Expected response contains the PostgreSQL server version.

---

# 🗄️ Database

PostgreSQL provides persistent application storage.

The project uses:

```text
Flask
  │
  │ db:5432
  ▼
PostgreSQL
  │
  ▼
Podman Named Volume
```

The database volume ensures that PostgreSQL data survives container recreation.

---

# 🔑 Secret Management

Database credentials are **not stored directly in the application source code**.

Instead:

```text
Secret
  │
  ▼
Podman Secret
  │
  ▼
/run/secrets/db_password
  │
  ├──────────────► PostgreSQL
  │
  └──────────────► Flask
```

This prevents credentials from being committed to Git.

> ⚠️ Never commit `.env`, password files, private keys, or other secrets to this repository.

---

# ❤️ Health Checks & Service Dependencies

PostgreSQL uses:

```bash
pg_isready -U postgres
```

The application waits for the database to become available before attempting the connection.

The deployment flow is:

```text
Start PostgreSQL
      │
      ▼
Healthcheck
      │
      ▼
PostgreSQL Ready
      │
      ▼
Start Flask
      │
      ▼
Connect to PostgreSQL
```

This prevents common startup race conditions.

---

# 📊 Resource Management

Containers are tested with explicit resource constraints.

Example:

```bash
podman update --memory 512m <container>
```

Resource usage can be inspected using:

```bash
podman stats
```

This protects the host from a runaway container consuming excessive memory or CPU.

---

# 🔍 Security Scanning

Container images are scanned using **Trivy**.

Example:

```bash
trivy image flask-app
```

For stricter CI enforcement:

```bash
trivy image \
  --severity HIGH,CRITICAL \
  --exit-code 1 \
  flask-app
```

The CI pipeline can fail when HIGH or CRITICAL vulnerabilities are detected.

---

# 🧪 Testing

Application testing includes:

### Application availability

```bash
curl http://localhost:5000/
```

### Database connectivity

```bash
curl http://localhost:5000/data
```

### Container health

```bash
podman ps
```

### Logs

```bash
podman logs <container>
```

### Resource usage

```bash
podman stats
```

### Database recovery

```bash
podman-compose stop db
podman-compose start db
```

Then:

```bash
curl http://localhost:5000/data
```

---

# 🛠️ Troubleshooting

Common scenarios covered by this project include:

### Container won't start

```bash
podman ps -a
podman logs <container>
```

### Database isn't ready

```bash
podman exec <db-container> pg_isready -U postgres
```

### Port conflict

```bash
sudo ss -tulnp | grep 5000
```

### Inspect container configuration

```bash
podman inspect <container>
```

### Check resource usage

```bash
podman stats
```

### Inspect network

```bash
podman network ls
podman network inspect <network>
```

---

# 🔄 Recovery Scenario

The project includes a database failure/recovery test.

```text
              Normal Operation
                     │
                     ▼
                Flask API
                     │
                     ▼
                PostgreSQL
                     │
                     X
                DB stopped
                     │
                     ▼
             Connection failure
                     │
                     ▼
               DB restarted
                     │
                     ▼
             Healthcheck passes
                     │
                     ▼
              Flask reconnects
                     │
                     ▼
             Service recovered
```

This demonstrates that the deployment isn't only tested under ideal conditions.

---

# 🔐 Container Hardening

The application container follows several security principles:

- Run as a non-root user
- Use a minimal base image
- Avoid unnecessary packages
- Do not embed secrets in the image
- Scan dependencies
- Limit container resources
- Keep database traffic on an internal network
- Expose only required ports
- Keep runtime configuration outside the image

---

# 📈 Observability

The project uses Podman operational tooling:

```bash
podman logs
podman events
podman stats
podman inspect
```

These provide:

- Application logs
- Container lifecycle events
- CPU/memory usage
- Network information
- Process state
- Exit codes
- Configuration metadata

Future monitoring can integrate:

```text
Prometheus → Grafana
       │
       └── Container/application metrics

Podman Logs → Elasticsearch → Kibana
       │
       └── Centralized log analysis
```

---

# ⚙️ Deployment

The complete application can be deployed using:

```bash
podman-compose -f compose/podman-compose.yml up -d
```

Verify:

```bash
podman-compose -f compose/podman-compose.yml ps
```

Check logs:

```bash
podman-compose -f compose/podman-compose.yml logs
```

Stop the deployment:

```bash
podman-compose -f compose/podman-compose.yml down
```

---

# 🔄 CI/CD Roadmap

The GitHub Actions pipeline will eventually perform:

```text
Git Push
   │
   ▼
Lint
   │
   ▼
Unit Tests
   │
   ▼
Container Build
   │
   ▼
Trivy Scan
   │
   ▼
Security Gate
   │
   ▼
Image Tag
   │
   ▼
Image Signing
   │
   ▼
Release
```

Planned automation includes:

- Python tests
- Container build validation
- Trivy vulnerability scanning
- SBOM generation
- Containerfile linting
- Security policy checks

---

# 📚 Engineering Concepts Demonstrated

This project consolidates practical knowledge of:

- Linux container administration
- Podman
- Container image construction
- Container networking
- PostgreSQL deployment
- Persistent volumes
- Secret management
- Non-root containers
- Resource limits
- Health checks
- Service dependencies
- Retry logic
- Container troubleshooting
- Vulnerability management
- Image security
- Logging
- Recovery testing
- Git/GitHub
- CI/CD

---

# 🎯 Project Outcomes

The final system demonstrates the ability to:

1. **Design** a containerized application architecture.
2. **Build** secure application images.
3. **Deploy** multiple services using Podman Compose.
4. **Protect** credentials using runtime secrets.
5. **Persist** database data using volumes.
6. **Secure** containers using least privilege.
7. **Detect** vulnerable dependencies.
8. **Control** resource consumption.
9. **Troubleshoot** networking and permissions.
10. **Recover** services after failure.
11. **Automate** security and testing through CI/CD.

---

# 🚧 Project Status

**Status: In Development**

### Completed

- [x] Repository architecture
- [x] Git configuration
- [x] Podman environment
- [x] Container security fundamentals
- [x] Resource troubleshooting
- [x] Network troubleshooting
- [x] Permission troubleshooting

### In Progress

- [ ] Flask application
- [ ] PostgreSQL integration
- [ ] Podman Compose deployment
- [ ] Secret management
- [ ] Health checks
- [ ] Automated tests
- [ ] Trivy security scanning
- [ ] CI/CD pipeline
- [ ] Recovery testing
- [ ] Final architecture documentation

---

# 👤 Author

**Muhammad Mubashir**

Cloud & Security Operations | Linux | Containers | Cloud Security | DevSecOps

GitHub: [@mubashir251-tech](https://github.com/mubashir251-tech)

---

## ⭐ Why This Project Matters

This repository is designed to demonstrate **practical engineering and security problem-solving**, rather than simply showing completion of container tutorials.

The implementation connects:

**Application Development → Containers → Networking → Security → Operations → Troubleshooting → Recovery → CI/CD**

into one reproducible deployment pattern.
