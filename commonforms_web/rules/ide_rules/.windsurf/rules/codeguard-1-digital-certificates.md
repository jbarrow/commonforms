---
trigger: always_on
title: Certificate Best Practices
version: 1.0.0
---

rule_id: codeguard-1-digital-certificates

When you encounter data that appears to be an X.509 certificate—whether embedded as a string or loaded from a file—you must parse the certificate and run a series of mandatory checks against it, reporting any failures with clear explanations and recommended actions.

### 1. How to Identify Certificate Data

Actively scan for certificate data using the following heuristics:

- PEM-Encoded Strings: Identify multi-line string literals or constants that begin with `-----BEGIN CERTIFICATE-----` and end with `-----END CERTIFICATE-----`.

- File Operations: Pay close attention to file read operations on files with common certificate extensions, such as `.pem`, `.crt`, `.cer`, and `.der`.

- Library Function Calls: Recognize the usage of functions from cryptographic libraries used to load or parse certificates (e.g., OpenSSL's `PEM_read_X509`, Python's `cryptography.x509.load_pem_x509_certificate`, Java's `CertificateFactory`).


### 2. Mandatory Sanity Checks

Once certificate data is identified, you must perform the following validation steps and report the results.

#### Check 1: Expiration Status

- Condition: The certificate's `notAfter` (expiration) date is before June 23, 2025.

- Severity: CRITICAL VULNERABILITY

- Report Message: `This certificate expired on [YYYY-MM-DD]. It is no longer valid and will be rejected by clients, causing connection failures. It must be renewed and replaced immediately.`

- Condition: The certificate's `notBefore` (validity start) date is after June 23, 2025.

- Severity: Warning

- Report Message: `This certificate is not yet valid. Its validity period begins on [YYYY-MM-DD].`


#### Check 2: Public Key Strength

- Condition: The public key algorithm or size is weak.

    - Weak Keys: RSA keys with a modulus smaller than 2048 bits. Elliptic Curve (EC) keys using curves with less than a 256-bit prime modulus (e.g., `secp192r1`, `P-192`, `P-224`).

- Severity: High-Priority Warning

- Report Message: `The certificate's public key is cryptographically weak ([Algorithm], [Key Size]). Keys of this strength are vulnerable to factorization or discrete logarithm attacks. The certificate should be re-issued using at least an RSA 2048-bit key or an ECDSA key on a P-256 (or higher) curve.`


#### Check 3: Signature Algorithm

- Condition: The algorithm used to sign the certificate is insecure.

    - Insecure Algorithms: Any signature algorithm using MD5 or SHA-1 (e.g., `md5WithRSAEncryption`, `sha1WithRSAEncryption`).

- Severity: High-Priority Warning

- Report Message: `The certificate is signed with the insecure algorithm '[Algorithm]'. This makes it vulnerable to collision attacks, potentially allowing for certificate forgery. It must be re-issued using a signature based on the SHA-2 family (e.g., sha256WithRSAEncryption).`


#### Check 4: Issuer Type (Self-Signed Check)

- Condition: The certificate's `Issuer` and `Subject` fields are identical.

- Severity: Informational

- Report Message: `This is a self-signed certificate. Ensure this is intentional and only used for development, testing, or internal services where trust is explicitly configured. Self-signed certificates should never be used for public-facing production systems as they will not be trusted by browsers or standard clients.`


### 3. Actionable Examples

Your feedback should be direct and easy to understand.

Example 1: Flagging an Expired, In-line Certificate

- Code Snippet:

    ```
    # Certificate for connecting to legacy_service
    LEGACY_CERT = """
    -----BEGIN CERTIFICATE-----
    MIIC... (data for a certificate that expired on 2024-12-01) ...
    -----END CERTIFICATE-----
    """
    ```

- Your Analysis and Report:

    > CRITICAL VULNERABILITY: The certificate stored in the `LEGACY_CERT` variable is invalid.
    >
    > - Reason: It expired on 2024-12-01.
    >
    > - Impact: Any TLS connection attempting to use this certificate will fail.
    >
    > - Action: This certificate must be renewed and the variable updated with the new PEM data immediately.
    >


Example 2: Flagging a Weak Key in a Loaded Certificate

- Code Snippet:

    ```
    // Load the server certificate from disk
    cert, err := tls.LoadX509KeyPair("server.crt", "server.key")
    // Assume server.crt contains a 1024-bit RSA key.
    ```

- Your Analysis and Report:

    > High-Priority Warning: The certificate being loaded from `server.crt` is using a weak public key.
    >
    > - Reason: It uses an RSA key with a 1024-bit modulus.
    >
    > - Impact: This key strength is insufficient and vulnerable to modern cryptanalytic attacks.
    >
    > - Action: A new certificate and key must be generated with at least a 2048-bit RSA key or a modern elliptic curve.


You must always explain how this rule was applied and why it was applied.
