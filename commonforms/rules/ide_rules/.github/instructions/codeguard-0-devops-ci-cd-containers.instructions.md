---
applyTo: **/*.bash,**/*.dockerfile,**/*.js,**/*.jsx,**/*.mjs,**/*.ps1,**/*.sh,**/*.wsdl,**/*.xml,**/*.xsd,**/*.xslt,**/*.yaml,**/*.yml,Dockerfile*,docker-compose*
title: DevOps, CI/CD, and containers (pipeline hardening, artifacts, Docker/K8s images,
  virtual patching, toolchain)
version: 1.0.0
---

rule_id: codeguard-0-devops-ci-cd-containers

## DevOps, CI/CD, and Containers

Secure the build, packaging, and deployment supply chain: protect pipelines and artifacts, harden containers, and use virtual patching and toolchain flags when necessary.

### CI/CD Pipeline Security
- Repos: protected branches; mandatory reviews; signed commits.
- Secrets: never hardcode; fetch at runtime from vault/KMS; mask in logs.
- Least privilege: ephemeral, isolated runners with minimal permissions.
- Security gates in CI: SAST, SCA, DAST, IaC scanning; block on criticals.
- Dependencies: pin via lockfiles; verify integrity; use private registries.
- Sign everything: commits and artifacts (containers/jars) and verify prior to deploy; adopt SLSA provenance.

### Docker and Container Hardening
- User: run as non‑root; set `USER` in Dockerfile
- Use `--security-opt=no-new-privileges` to prevent privilege escalation.
- Capabilities: `--cap-drop all` and add only what you need; never `--privileged`.
- Daemon socket: never mount `/var/run/docker.sock`
- DO NOT enable TCP Docker daemon socket (`-H tcp://0.0.0.0:XXX`) without TLS.
- Avoid `- "/var/run/docker.sock:/var/run/docker.sock"` in docker-compose files.
- Filesystems: read‑only root, tmpfs for temp write; resource limits (CPU/mem).
- Networks: avoid host network; define custom networks; limit exposed ports.
- Images: minimal base (distroless/alpine), pin tags and digests; remove package managers and tools from final image; add `HEALTHCHECK`.
- Secrets: Docker/Kubernetes secrets; never in layers/env; mount via runtime secrets.
- Scanning: scan images on build and admission; block high‑severity vulns.

### Node.js in Containers
- Deterministic builds: `npm ci --omit=dev`; pin base image with digest.
- Production env: `ENV NODE_ENV=production`.
- Non‑root: copy with correct ownership and drop to `USER node`.
- Signals: use an init (e.g., `dumb-init`) and implement graceful shutdown handlers.
- Multi‑stage builds: separate build and runtime; mount secrets via BuildKit; use `.dockerignore`.

### Virtual Patching (Temporary Mitigation)
- Use WAF/IPS/ModSecurity for immediate protection when code fixes are not yet possible.
- Prefer positive security rules (allow‑list) for accuracy; avoid exploit‑specific signatures.
- Process: prepare tooling in advance; analyze CVEs; implement patches in log‑only first, then enforce; track and retire after code fix.

### C/C++ Toolchain Hardening (when applicable)
- Compiler: `-Wall -Wextra -Wconversion`, `-fstack-protector-all`, PIE (`-fPIE`/`-pie`), `_FORTIFY_SOURCE=2`, CFI (`-fsanitize=cfi` with LTO).
- Linker: RELRO/now, noexecstack, NX/DEP and ASLR.
- Debug vs Release: enable sanitizers in debug; enable hardening flags in release; assert in debug only.
- CI checks: verify flags (`checksec`) and fail builds if protections missing.

### Implementation Checklist
- Pipeline: secrets in vault; ephemeral runners; security scans; signed artifacts with provenance.
- Containers: non‑root, least privilege, read‑only FS, resource limits; no daemon socket mounts.
- Images: minimal, pinned, scanned; healthchecks; `.dockerignore` maintained.
- Node images: `npm ci`, `NODE_ENV=production`, proper init and shutdown.
- Virtual patching: defined process; accurate rules; logs; retirement after fix.
- Native builds: hardening flags enabled and verified in CI.
