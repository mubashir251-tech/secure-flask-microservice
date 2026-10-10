# 🔐 Secure Flask Microservice Platform

> **Production-style Flask + PostgreSQL microservice secured with Podman, runtime secrets, least-privilege containers, vulnerability scanning, SBOM generation, image signing, automated tests, and GitHub Actions CI.**

[![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-black?logo=flask)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue?logo=postgresql)](https://www.postgresql.org/)
[![Podman](https://img.shields.io/badge/Container-Podman-purple?logo=podman)](https://podman.io/)
[![Trivy](https://img.shields.io/badge/Security-Trivy-red?logo=aquasecurity)](https://trivy.dev/)
[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-black?logo=githubactions)](https://github.com/features/actions)

---

## 📌 Project Overview

This project demonstrates how to **build, secure, test, scan, sign, deploy, troubleshoot, and operate a multi-container Flask microservice** backed by PostgreSQL.

It is intentionally designed as an engineering project rather than a basic Flask or container tutorial.

### Business Scenario

A small business needs an internal/backend API that must:

- Run reliably in containers
- Store application data persistently
- Protect database credentials
- Avoid root execution
- Restrict container privileges
- Limit CPU and memory consumption
- Provide health and database-readiness endpoints
- Detect vulnerable dependencies
- Generate a software bill of materials
- Verify container image integrity
- Support reproducible deployment through Compose
- Be tested automatically in CI
- Recover cleanly from service interruptions

---

# 🏗️ Architecture

```text
                         Client
                           │
                           │ HTTP
                           ▼
              ┌─────────────────────────┐
              │       Flask API         │
              │       Gunicorn          │
              │                         │
              │  Non-root UID 10001     │
              │  Read-only filesystem   │
              │  CAP_DROP=ALL           │
              │  No-new-privileges      │
              │  CPU / memory limits    │
              └────────────┬────────────┘
                           │
                           │ PostgreSQL
                           │ private network
                           ▼
              ┌─────────────────────────┐
              │      PostgreSQL 15      │
              │                         │
              │  Healthcheck            │
              │  Secret password        │
              │  Persistent volume      │
              └────────────┬────────────┘
                           │
                           ▼
                    Podman Volume
```

### Security / Supply-Chain Flow

```text
Source Code
    │
    ▼
Podman Build
    │
    ├──────────────► Automated Tests
    │
    ▼
Container Image
    │
    ├──────────────► Trivy Vulnerability Scan
    │
    ├──────────────► CycloneDX SBOM
    │
    ▼
Image Registry
    │
    ▼
Cosign Signature
    │
    ▼
Digest-based Verification
    │
    ▼
Deployment
```

---

# 🔒 Security Architecture

The application container is deliberately hardened using multiple independent controls.

| Control | Implementation | Verified |
|---|---|---|
| Non-root execution | UID/GID `10001:10001` | ✅ |
| Secret management | Podman secret | ✅ |
| No password in source | `db_password` mounted at runtime | ✅ |
| Minimal base image | `python:3.12-slim-bookworm` | ✅ |
| CPU limit | `0.5` CPU | ✅ |
| Memory limit | `256 MB` | ✅ |
| No privilege escalation | `no-new-privileges` | ✅ |
| Linux capabilities | `CAP_DROP=ALL` | ✅ |
| Root filesystem | Read-only | ✅ |
| Private service network | Podman bridge network | ✅ |
| PostgreSQL healthcheck | `pg_isready` | ✅ |
| Application health | `/health` | ✅ |
| Database readiness | `/ready` | ✅ |
| Vulnerability scanning | Trivy | ✅ |
| SBOM | CycloneDX | ✅ |
| Image signing | Cosign | ✅ |
| Digest verification | Cosign + immutable digest | ✅ |
| Automated tests | pytest | ✅ |
| CI | GitHub Actions | ✅ |

---

# 🛡️ Runtime Container Hardening

The Flask container currently runs with:

```text
User             10001:10001
Memory           256 MB
CPU              0.5
Read-only root   true
No-new-privs     enabled
Capabilities     dropped
```

Verified runtime configuration:

```bash
podman inspect compose_web_1 \
  --format 'User={{.Config.User}} Memory={{.HostConfig.Memory}} CPUs={{.HostConfig.NanoCpus}} Readonly={{.HostConfig.ReadonlyRootfs}} Security={{json .HostConfig.SecurityOpt}} CapDrop={{json .HostConfig.CapDrop}}'
```

Example verified result:

```text
User=10001:10001
Memory=268435456
CPUs=500000000
Readonly=true
Security=["no-new-privileges"]
CapDrop=["CAP_CHOWN","CAP_DAC_OVERRIDE","CAP_FOWNER","CAP_FSETID","CAP_KILL","CAP_NET_BIND_SERVICE","CAP_SETFCAP","CAP_SETGID","CAP_SETPCAP","CAP_SETUID","CAP_SYS_CHROOT"]
```

### Why these controls matter

**Non-root**

The application does not run as root, reducing the impact of a container compromise.

**Read-only filesystem**

The container root filesystem cannot be modified during normal runtime.

**No-new-privileges**

Processes cannot gain additional privileges through privilege-escalation mechanisms.

**Capability dropping**

The application does not require the default Linux capabilities, so they are explicitly removed.

**Resource limits**

CPU and memory limits reduce the impact of runaway application processes and resource exhaustion.

---

# 🔑 Secret Management

The database password is provided through a Podman secret rather than being embedded in the application image.

```text
                    Podman Secret
                         │
                         ▼
                 /run/secrets/db_password
                    │             │
                    ▼             ▼
               PostgreSQL       Flask
```

The Flask application supports the secret-file pattern:

```text
/run/secrets/db_password
```

and falls back to an environment variable for local development.

### Security rule

Never commit:

```text
.env
password files
private keys
certificates
credentials
```

to Git.

---

# 🧪 Application

The service is implemented with:

- Python 3.12
- Flask 3.1.3
- Gunicorn 22.0.0
- PostgreSQL 15
- psycopg2-binary 2.9.9

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Basic application status |
| `/health` | GET | Application health |
| `/ready` | GET | PostgreSQL readiness |
| `/data` | GET | PostgreSQL version/connectivity |
| `/users` | GET | Retrieve application users |

### Health

```bash
curl http://localhost:5001/health
```

Expected:

```json
{
  "service": "secure-flask-microservice",
  "status": "healthy"
}
```

### Readiness

```bash
curl http://localhost:5001/ready
```

Expected:

```json
{
  "database": "available",
  "status": "ready"
}
```

### Users

```bash
curl http://localhost:5001/users
```

The endpoint returns the users stored in PostgreSQL.

---

# 🗄️ PostgreSQL

PostgreSQL is deployed as a separate container on the private Podman network.

```text
Flask
  │
  │ db:5432
  ▼
PostgreSQL
  │
  ▼
compose_pgdata
```

The named volume allows database data to survive container recreation.

Database initialization is handled by:

```text
database/init.sql
```

The initialization script creates the `users` table and inserts a demo user when required.

---

# ❤️ Health Checks and Dependencies

PostgreSQL uses:

```bash
pg_isready -U postgres -d mydb
```

The Compose deployment uses the database health state before starting the web service.

The readiness endpoint independently tests the actual PostgreSQL connection.

This separates two important concepts:

```text
/health
   │
   └── Is the application process alive?

/ready
   │
   └── Can the application reach PostgreSQL?
```

---

# 🧪 Automated Testing

The project includes pytest tests covering:

- Application availability
- Health endpoint
- Database readiness failure handling
- Database connectivity failure handling
- User query failure handling

Run tests using the dedicated test image:

```bash
podman build \
  -f container/Containerfile \
  -t localhost/secure-flask-microservice:ci .
```

```bash
podman build \
  --build-arg BASE_IMAGE=localhost/secure-flask-microservice:ci \
  -t localhost/secure-flask-microservice:test \
  -f container/Containerfile.test .
```

```bash
podman run --rm \
  localhost/secure-flask-microservice:test
```

Current verified result:

```text
5 passed
```

The production image does not contain pytest.

---

# 🔍 Vulnerability Scanning

Trivy is used to scan the production image.

CI exports the rootless Podman image to an archive before scanning:

```bash
podman save \
  -o secure-flask-microservice.tar \
  localhost/secure-flask-microservice:ci
```

Then Trivy scans the archive:

```bash
trivy image \
  --input secure-flask-microservice.tar \
  --scanners vuln \
  --severity HIGH,CRITICAL \
  --ignore-unfixed
```

### Current scan status

The final production image was scanned with Trivy using HIGH and CRITICAL severity levels with unfixed vulnerabilities ignored.

**Result: 0 HIGH/CRITICAL vulnerabilities detected** with `--ignore-unfixed` enabled. This result applies to the scanned image and Trivy's available vulnerability data at the time of the scan; it is not a guarantee that the image has no vulnerabilities.

The final scan covered:

- Debian 12.15 base OS
- Flask
- Gunicorn
- psycopg2-binary
- Jinja2
- Werkzeug
- Other installed Python runtime dependencies

The production image also removes `pip` after dependency installation, reducing unnecessary runtime tooling and eliminating the previously detected vulnerabilities associated with pip-vendored packages.

This demonstrates an important security engineering principle:

> A security scan is evidence, not a decorative badge. Findings must be reviewed, tracked, and remediated according to risk and availability of fixes.

---

# 📦 Software Bill of Materials

The CI pipeline generates a CycloneDX SBOM:

```bash
trivy image \
  --input secure-flask-microservice.tar \
  --format cyclonedx \
  --output sbom.cdx.json
```

The SBOM is uploaded to GitHub Actions as a build artifact.

It provides visibility into the software components contained in the image and supports future dependency and vulnerability management.

---

# ✍️ Image Signing and Verification

Cosign is used to demonstrate container image signing and verification.

The project uses a local OCI registry for the signing lab:

```text
localhost:5000
```

The image is pushed to the registry and signed using Cosign.

Verification is performed using the public key.

### Strong verification model

The final hardened image was pushed to the local OCI registry and signed with Cosign. Verification was performed against the immutable digest rather than relying only on a mutable tag.

**Final verified image digest:**

```text
sha256:e3986224595567d92901cdd4e417a2a15d5af1d530238f7ad9612487338bd645
```

#### Final verification evidence

| Check | Result |
|---|---|
| Sign the final hardened image with Cosign | Passed |
| Verify with the corresponding public key | Passed |
| Validate the digest and Cosign claims | Passed |
| Attempt verification with an unrelated public key | Rejected |
| Keep the private signing key outside the repository | Maintained |

The unrelated-key attempt was rejected with a transparency-log certificate mismatch. This demonstrates rejection in that verification flow; it should not be presented as an isolated test of every possible signature-validation failure.

Conceptually:

```text
Image Tag
   │
   ▼
Registry Manifest
   │
   ▼
Immutable Digest
   │
   ▼
Cosign Signature
   │
   ▼
Public-Key Verification
```

### Important limitation

The current signing setup is a **local security demonstration**, not a production trust architecture. The registry uses HTTP with TLS verification disabled for this lab.

A valid signature binds the signing identity to the signed image digest; it does not, by itself, prove that the image is vulnerability-free or safe to deploy.

Production deployment should move toward:

- TLS-enabled trusted registry
- protected signing keys
- CI-controlled signing
- keyless Sigstore workflows where appropriate
- signature verification as a deployment policy

---

# 🏗️ Container Build

Production image:

```text
container/Containerfile
```

The image uses:

```text
python:3.12-slim-bookworm
```

The application is installed with pinned dependencies and served using Gunicorn.

The container creates:

```text
appgroup → GID 10001
appuser  → UID 10001
```

The production container therefore does not require root privileges.

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
│   └── Containerfile.test
│
├── compose/
│   └── podman-compose.yml
│
├── tests/
│   ├── requirements.txt
│   └── test_app.py
│
├── .github/
│   └── workflows/
│       └── ci.yml
│
├── .gitignore
└── README.md
```

---

# 🚀 Deployment

Create the required external Podman secret before deployment:

```bash
printf '%s' 'YOUR_DATABASE_PASSWORD' | \
  podman secret create db_password -
```

Start the application:

```bash
podman-compose -f compose/podman-compose.yml up -d
```

Check containers:

```bash
podman ps
```

Check logs:

```bash
podman-compose -f compose/podman-compose.yml logs
```

Test:

```bash
curl http://localhost:5001/health
curl http://localhost:5001/ready
```

Stop the deployment:

```bash
podman-compose -f compose/podman-compose.yml down
```

### Current local port

The Flask container listens on port `5000`.

The current Compose deployment maps:

```text
Host 5001 → Container 5000
```

Port `5001` is used because the local OCI registry used for image-signing exercises occupies host port `5000`.

---

# 📊 Resource Management

The web container is configured with:

```yaml
mem_limit: 256m
cpus: 0.5
```

Inspect:

```bash
podman stats --no-stream compose_web_1
```

Inspect configured limits:

```bash
podman inspect compose_web_1 \
  --format 'Memory={{.HostConfig.Memory}} CPUs={{.HostConfig.NanoCpus}}'
```

Expected:

```text
Memory=268435456
CPUs=500000000
```

---

# 🔧 Troubleshooting and Engineering Lessons

This project included real troubleshooting rather than only successful commands.

Problems investigated during development included:

- Rootless Podman image visibility to Trivy
- CI test-image dependency
- Local registry and host-port conflicts
- Podman network recreation
- Container-to-container PostgreSQL connectivity
- Health/readiness behavior
- Resource-limit verification
- Runtime security option verification
- Compose feature compatibility

### Important lesson: verify generated runtime configuration

A Compose file can contain a setting without the installed Compose implementation actually translating it into the runtime command.

For example, `pids_limit` was tested but `podman-compose 1.0.6` did not generate the corresponding Podman option. The setting was therefore removed instead of being falsely documented as active.

This is an intentional engineering decision:

> **Only claim a security control after verifying it at runtime.**

---

# 📈 Operational Observability

Podman provides useful operational information through:

```bash
podman logs compose_web_1
podman events
podman stats
podman inspect compose_web_1
```

These support:

- Application log inspection
- Container lifecycle investigation
- CPU/memory monitoring
- Runtime configuration verification
- Troubleshooting
- Incident investigation

Future projects can extend this into:

```text
Prometheus → Grafana
       │
       └── Metrics

Podman Logs → Elasticsearch → Kibana
       │
       └── Centralized Logs
```

Those are **future extensions**, not claimed as part of the current implementation.

---

# 🔄 Recovery Testing

The deployment is designed to tolerate PostgreSQL interruptions.

Example recovery workflow:

```bash
podman-compose -f compose/podman-compose.yml stop db
```

Check application behavior:

```bash
curl http://localhost:5001/ready
```

The readiness endpoint should report that the database is unavailable.

Restart PostgreSQL:

```bash
podman-compose -f compose/podman-compose.yml start db
```

Wait for health:

```bash
podman ps
```

Then verify:

```bash
curl http://localhost:5001/ready
```

Expected:

```json
{
  "database": "available",
  "status": "ready"
}
```

---

# 🔄 CI/CD Pipeline

GitHub Actions currently performs:

```text
Git Push / Pull Request
          │
          ▼
     Checkout Code
          │
          ▼
       Install Podman
          │
          ▼
   Build Production Image
          │
          ▼
      Build Test Image
          │
          ▼
     Run pytest Tests
          │
          ▼
       Install Trivy
          │
          ▼
   Export Podman Image
          │
          ├──────────────► Trivy Vulnerability Scan
          │
          └──────────────► CycloneDX SBOM
                                  │
                                  ▼
                         Upload CI Artifact
```

Workflow:

```text
.github/workflows/ci.yml
```

The workflow runs on:

- Pushes to `main`
- Pull requests targeting `main`

The current CI pipeline has been successfully executed through the build, test, security scan, and SBOM stages.

---

# 🧰 Technology Stack

| Layer | Technology |
|---|---|
| Application | Python 3.12 |
| Web Framework | Flask 3.1.3 |
| WSGI Server | Gunicorn 22.0.0 |
| Database | PostgreSQL 15 |
| Container Runtime | Podman 4.9.3 |
| Compose | podman-compose 1.0.6 |
| Networking | Podman bridge network |
| Persistence | Podman named volume |
| Secrets | Podman Secrets |
| Testing | pytest |
| Vulnerability Scanner | Trivy 0.75.0 |
| SBOM | CycloneDX |
| Image Signing | Cosign 3.1.3 |
| CI/CD | GitHub Actions |
| Host | Ubuntu Linux |

---

# 📚 Engineering Concepts Demonstrated

This project brings together practical skills in:

- Linux container administration
- Podman
- Containerfile design
- Python application packaging
- Gunicorn
- PostgreSQL
- Container networking
- Persistent storage
- Runtime secret management
- Non-root containers
- Linux capability management
- `no-new-privileges`
- Read-only filesystems
- CPU and memory limits
- Healthchecks
- Readiness checks
- Automated testing
- Vulnerability management
- SBOM generation
- Container image signing
- Digest verification
- CI/CD
- Troubleshooting
- Recovery testing
- Git/GitHub

---

# 🎯 Project Outcomes

The project demonstrates the ability to:

1. **Design** a multi-container application architecture.
2. **Build** a production-style Flask container.
3. **Deploy** Flask and PostgreSQL with Podman Compose.
4. **Protect** credentials using runtime secrets.
5. **Run** the application without root privileges.
6. **Restrict** container capabilities.
7. **Prevent** privilege escalation.
8. **Make** the container filesystem read-only.
9. **Limit** CPU and memory consumption.
10. **Test** application behavior automatically.
11. **Scan** container dependencies for vulnerabilities.
12. **Generate** an SBOM.
13. **Sign and verify** a container image.
14. **Troubleshoot** container networking and runtime issues.
15. **Automate** security checks through GitHub Actions.
16. **Document** real engineering limitations rather than hiding them.

---

## Release Validation

The Secure Flask Microservice has undergone local release validation covering CI, image integrity, application functionality, database connectivity, and container runtime security.

### 1. CI and Repository Validation

| Check | Result |
|---|---|
| GitHub Actions workflow for commit `3c35f96` | Passed |
| Git working tree | Clean |
| Local `main` and `origin/main` | Synchronized |
| Application test suite | 5 tests passed |

### 2. Container Image Integrity

The hardened container image was published to a local OCI registry and signed using Cosign.

| Check | Result |
|---|---|
| Registry API availability | Passed |
| Registry manifest digest | Matched the previously signed digest |
| Cosign signature verification | Passed |
| Public-key verification | Passed |
| Signature claims validation | Passed |
| Transparency log inclusion verification | Passed |

**Verified image digest:**

`sha256:e3986224595567d92901cdd4e417a2a15d5af1d530238f7ad9612487338bd645`

The digest identifies the exact image manifest verified during this validation. The signature establishes a verifiable relationship between the image digest and the signing key; it does not independently establish that the image is vulnerability-free or safe.

### 3. Application and Database Validation

The running application was tested through its HTTP endpoints.

| Endpoint | Observed result |
|---|---|
| `/` | HTTP 200 OK |
| `/health` | HTTP 200 OK |
| `/ready` | HTTP 200 OK; database available |
| `/data` | HTTP 200 OK; PostgreSQL version returned |
| `/users` | HTTP 200 OK; user records returned |

The PostgreSQL container reported a healthy status, and the application successfully retrieved database records.

### 4. Container Runtime Security

Runtime inspection confirmed the following controls on the web container:

| Control | Observed configuration |
|---|---|
| Container identity | UID/GID `10001:10001` |
| Root filesystem | Read-only |
| Linux capabilities | Effective, permitted, inheritable, and bounding sets were zero |
| `no-new-privileges` | Enabled |
| Memory limit | 256 MiB |
| CPU limit | 0.5 CPU |
| Database password environment variable | Not present in the web process environment |

These results document the configuration observed during the lab validation. They do not replace broader security testing or production deployment checks.

### 5. Vulnerability Scanning and SBOM

The hardened image was scanned using Trivy with the following options:

- Scanners: vulnerabilities
- Severity threshold: HIGH and CRITICAL
- Unfixed vulnerabilities: ignored
- Result: 0 HIGH/CRITICAL vulnerabilities detected under the configured scan options

A CycloneDX Software Bill of Materials (SBOM) was also generated and uploaded as a CI artifact.

Scan results depend on the image version, scanner configuration, and vulnerability database available at scan time. The result does not mean the image contains no vulnerabilities.

### 6. Known Limitations and Production Follow-Up

The following items remain before a production deployment:

- **Secret permissions:** The database secret is mounted inside the web container with mode `0444`, making it readable by all users in that container. Investigate a supported least-privilege secret-mount configuration.
- **Registry transport:** The local lab registry uses HTTP with TLS verification disabled for the signing workflow. Use authenticated TLS for production.
- **Signing trust:** Protect signing keys and enforce signature verification at deployment time. Consider an appropriate CI-controlled or keyless signing workflow.
- **Deployment validation:** Test the deployment environment, monitoring, logging, recovery, and security policies before production use.
- **Ongoing scanning:** Rebuild and rescan images as dependencies and vulnerability intelligence change.

### Validation Status

**Status: Lab-validated; production hardening remains in progress.**

This project demonstrates container hardening, automated testing, vulnerability scanning, SBOM generation, image signing, and signature verification in a reproducible lab environment.

# 🚧 Project Status

**Status: Core implementation and local lab validation complete. Production trust enhancements and Kubernetes deployment remain future work.**

### Completed

- [x] Flask application
- [x] PostgreSQL integration
- [x] Podman containerization
- [x] Podman Compose deployment
- [x] Persistent database volume
- [x] Runtime secret management
- [x] Health endpoint
- [x] Database readiness endpoint
- [x] Automated pytest tests
- [x] Non-root container
- [x] CPU and memory limits
- [x] `no-new-privileges`
- [x] `CAP_DROP=ALL`
- [x] Read-only root filesystem
- [x] Trivy vulnerability scanning
- [x] CycloneDX SBOM generation
- [x] Cosign image signing
- [x] Digest-based signature verification
- [x] GitHub Actions CI
- [x] Runtime troubleshooting
- [x] Recovery testing
- [x] Security hardening verification

### Intentionally Not Claimed

- [ ] Production Kubernetes deployment
- [ ] Production TLS registry
- [ ] Keyless production signing
- [ ] Prometheus/Grafana monitoring
- [ ] Centralized Elasticsearch/Kibana logging
- [ ] Runtime PID limit through current `podman-compose` implementation

These belong to future project iterations rather than being presented as completed features.

---

# 🔮 Future Roadmap

Possible future evolution:

### Phase 2 — Container Security Pipeline

```text
Git
 │
 ▼
Build
 │
 ├── Tests
 ├── Trivy
 ├── SBOM
 ├── Policy Checks
 └── Image Signing
 │
 ▼
Trusted Registry
 │
 ▼
Verified Deployment
```

### Phase 3 — Kubernetes Platform

Move the application to:

- Kubernetes
- Helm
- NetworkPolicies
- Kubernetes Secrets
- Pod Security
- Resource Requests/Limits
- Liveness/Readiness probes
- Image signature verification

### Phase 4 — Observability

Add:

- Prometheus
- Grafana
- Centralized logging
- Alerting
- Application metrics

---

# 👤 Author

**Muhammad Mubashir**

Cloud & Security Operations | Linux | Containers | Cloud Security | DevSecOps

GitHub: [@mubashir251-tech](https://github.com/mubashir251-tech)

---

# ⭐ Why This Project Matters

This repository is designed to demonstrate **practical engineering and security problem-solving**, not simply completion of container tutorials.

The project connects:

```text
Application Development
        │
        ▼
Containers
        │
        ▼
Networking
        │
        ▼
Security
        │
        ▼
Testing
        │
        ▼
Supply-Chain Security
        │
        ▼
CI/CD
        │
        ▼
Operations & Troubleshooting
        │
        ▼
Recovery
```

The result is a reproducible, security-focused microservice platform that can serve as a foundation for the next stage of the user's container-security and Kubernetes learning path.
