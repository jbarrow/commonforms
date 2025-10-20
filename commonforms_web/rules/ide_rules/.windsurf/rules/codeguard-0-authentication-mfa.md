---
trigger: glob
globs: **/*.c,**/*.go,**/*.h,**/*.java,**/*.js,**/*.jsx,**/*.kt,**/*.kts,**/*.m,**/*.mjs,**/*.php,**/*.py,**/*.pyi,**/*.pyx,**/*.rb,**/*.swift,**/*.ts,**/*.tsx
title: Authentication and MFA best practices (passwords, MFA, OAuth/OIDC, SAML, recovery,
  tokens)
version: 1.0.0
---

rule_id: codeguard-0-authentication-mfa

## Authentication & MFA

Build a resilient, user-friendly authentication system that resists credential attacks, protects secrets, and supports strong, phishing-resistant MFA and secure recovery.

### Account Identifiers and UX
- Use non-public, random, and unique internal user identifiers. Allow login via verified email or username.
- Always return generic error messages (e.g., "Invalid username or password"). Keep timing consistent to prevent account enumeration.
- Support password managers: `<input type="password">`, allow paste, no JS blocks.

### Password Policy
- Accept passphrases and full Unicode; minimum 8 characters; avoid composition rules. Set only a reasonable maximum length (64+).
- Check new passwords against breach corpora (e.g., k‑anonymity APIs); reject breached/common passwords.

### Password Storage (Hashing)
- Hash, do not encrypt. Use slow, memory‑hard algorithms with unique per‑user salts and constant‑time comparison.
- Preferred order and parameters (tune to your hardware; target <1s on server):
  - Argon2id: m=19–46 MiB, t=2–1, p=1 (or equivalent security trade‑offs)
  - scrypt: N=2^17, r=8, p=1 (or equivalent)
  - bcrypt (legacy only): cost ≥10, be aware of 72‑byte input limit
  - PBKDF2 (FIPS): PBKDF2‑HMAC‑SHA‑256 ≥600k, or SHA‑1 ≥1.3M
- Optional pepper: store outside DB (KMS/HSM); if used, apply via HMAC or pre‑hashing. Plan for user resets if pepper rotates.
- Unicode and null bytes must be supported end‑to‑end by the library.

### Authentication Flow Hardening
- Enforce TLS for all auth endpoints and token transport; enable HSTS.
- Implement rate limits per IP, account, and globally; add proof‑of‑work or CAPTCHA only as last resort.
- Lockouts/throttling: progressive backoff; avoid permanent lockout via resets/alerts.
- Uniform responses and code paths to reduce oracle/timing signals.

### Multi‑Factor Authentication (MFA)
- Adopt phishing‑resistant factors by default for sensitive accounts: passkeys/WebAuthn (FIDO2) or hardware U2F.
- Acceptable: TOTP (app‑based), smart cards with PIN. Avoid for sensitive use: SMS/voice, email codes; never rely on security questions.
- Require MFA for: login, password/email changes, disabling MFA, privilege elevation, high‑value transactions, new devices/locations.
- Risk‑based MFA signals: new device, geo‑velocity, IP reputation, unusual time, breached credentials.
- MFA recovery: provide single‑use backup codes, encourage multiple factors, and require strong identity verification for resets.
- Handle failed MFA: offer alternative enrolled methods, notify users of failures, and log context (no secrets).

### Federation and Protocols (OAuth 2.0 / OIDC / SAML)
- Use standard protocols only; do not build your own.
- OAuth 2.0/OIDC:
  - Prefer Authorization Code with PKCE for public/native apps; avoid Implicit and ROPC.
  - Validate state and nonce; use exact redirect URI matching; prevent open redirects.
  - Constrain tokens to audience/scope; use DPoP or mTLS for sender‑constraining when possible.
  - Rotate refresh tokens; revoke on logout or risk signals.
- SAML:
  - TLS 1.2+; sign responses/assertions; encrypt sensitive assertions.
  - Validate issuers, InResponseTo, timestamps (NotBefore/NotOnOrAfter), Recipient; verify against trusted keys.
  - Prevent XML signature wrapping with strict schema validation and hardened XPath selection.
  - Keep response lifetimes short; prefer SP‑initiated flows; validate RelayState; implement replay detection.

### Tokens (JWT and Opaque)
- Prefer opaque server‑managed tokens for simplicity and revocation. If using JWTs:
  - Explicitly pin algorithms; reject "none"; validate iss/aud/exp/iat/nbf; use short lifetimes and rotation.
  - Store secrets/keys securely (KMS/HSM). Use strong HMAC secrets or asymmetric keys; never hardcode.
  - Consider binding tokens to a client context (e.g., fingerprint hash in cookie) to reduce replay.
  - Implement denylist/allowlist for revocation on logout and critical events.

### Recovery and Reset
- Return the same response for existing and non‑existing accounts (no enumeration). Normalize timing.
- Generate 32+ byte, CSPRNG tokens; single‑use; store as hashes; short expiry.
- Use HTTPS reset links to pinned, trusted domains; add referrer policy (no‑referrer) on UI.
- After reset: require re‑authentication, rotate sessions, and do not auto‑login.
- Never lock accounts due to reset attempts; rate‑limit and monitor instead.

### Administrative and Internal Accounts
- Separate admin login from public forms; enforce stronger MFA, device posture checks, IP allowlists, and step‑up auth.
- Use distinct session contexts and stricter timeouts for admin operations.

### Monitoring and Signals
- Log auth events (failures/successes, MFA enroll/verify, resets, lockouts) with stable fields and correlation IDs; never log secrets or raw tokens.
- Detect credential stuffing: high failure rates, many IPs/agents, impossible travel. Notify users of new device logins.

### Implementation Checklist
- Passwords: Argon2id (preferred) with per‑user salt, constant‑time verify; breached password checks on change/set.
- MFA: WebAuthn/passkeys or hardware tokens for high‑risk; TOTP as fallback; secure recovery with backup codes.
- Federation: Authorization Code + PKCE; strict redirect URI validation; audience/scope enforced; token rotation.
- Tokens: short‑lived, sender‑constrained where possible; revocation implemented; secrets in KMS/HSM.
- Recovery: single‑use, hashed, time‑boxed tokens; consistent responses; re‑auth required after reset; sessions rotated.
- Abuse: rate limits, throttling, and anomaly detection on auth endpoints; uniform error handling.
- Admin: isolated flows with stricter policies and device checks.

### Test Plan
- Unit/integration tests for login, MFA enroll/verify, resets, and lockouts with uniform errors.
- Protocol tests: PKCE, state/nonce, redirect URI validation, token audience/scope.
- Dynamic tests for credential stuffing resistance and token replay; validate revocation after logout and role change.
