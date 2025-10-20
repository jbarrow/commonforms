---
trigger: glob
globs: **/*.js,**/*.jsx,**/*.m,**/*.mjs,**/*.yaml,**/*.yml
title: Privacy & data protection (minimization, classification, encryption, rights,
  transparency)
version: 1.0.0
---

rule_id: codeguard-0-privacy-data-protection

- Implement strong cryptography, enforce HTTPS with HSTS, enable certificate pinning,
and provide user privacy features to protect data and anonymity.
- Use strong, up-to-date cryptographic algorithms for data in transit and at rest; securely hash passwords with established libraries.
- Enforce HTTPS exclusively and implement HTTP Strict Transport Security (HSTS).
- Implement certificate pinning to prevent man-in-the-middle attacks even if CAs are compromised.
- Minimize IP address leakage by blocking third-party external content loading where feasible.
- Maintain transparency by informing users about privacy limitations and data handling policies.
- Implement privacy-focused audit trails and access logging.
- Return "Invalid username or password" to prevent account enumeration
- Use Argon2 or bcrypt with unique salts per user
- Store sessions server-side with cryptographically random IDs
