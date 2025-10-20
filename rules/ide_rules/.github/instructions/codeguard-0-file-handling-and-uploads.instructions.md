---
applyTo: **/*.c,**/*.go,**/*.h,**/*.java,**/*.js,**/*.jsx,**/*.mjs,**/*.php,**/*.py,**/*.pyi,**/*.pyx,**/*.rb,**/*.ts,**/*.tsx
title: Secure file handling & uploads (validation, storage isolation, scanning, safe
  delivery)
version: 1.0.0
---

rule_id: codeguard-0-file-handling-and-uploads

## File Upload Security Guidelines

This rule advises on secure file upload practices to prevent malicious file attacks and protect system integrity:

- Extension Validation
  - List allowed extensions only for business-critical functionality.
  - Ensure input validation is applied before validating extensions.
  - Avoid double extensions (e.g., `.jpg.php`) and null byte injection (e.g., `.php%00.jpg`).
  - Use allowlist approach rather than denylist for file extensions.
  - Validate extensions after decoding filename to prevent bypass attempts.

- Content Type and File Signature Validation
  - Never trust client-supplied Content-Type headers as they can be spoofed.
  - Validate file signatures (magic numbers) in conjunction with Content-Type checking.
  - Implement allowlist approach for MIME types as a quick protection layer.
  - Use file signature validation but not as a standalone security measure.

- Filename Security
  - Generate random filenames (UUID/GUID) instead of using user-supplied names.
  - If user filenames required, implement maximum length limits.
  - Restrict characters to alphanumeric, hyphens, spaces, and periods only.
  - Prevent leading periods (hidden files) and sequential periods (directory traversal).
  - Avoid leading hyphens or spaces for safer shell script processing.

- File Content Validation
  - For images, apply image rewriting techniques to destroy malicious content.
  - For Microsoft documents, use Apache POI for validation.
  - Avoid ZIP files due to numerous attack vectors.
  - Implement manual file review in sandboxed environments when resources allow.
  - Integrate antivirus scanning and Content Disarm & Reconstruct (CDR) for applicable file types.

- Storage Security
  - Store files on different servers for complete segregation when possible.
  - Store files outside webroot with administrative access only.
  - If storing in webroot, set write-only permissions with proper access controls.
  - Use application handlers that map IDs to filenames for public access.
  - Consider database storage for specific use cases with DBA expertise.

- Access Control and Authentication
  - Require user authentication before allowing file uploads.
  - Implement proper authorization levels for file access and modification.
  - Set filesystem permissions on principle of least privilege.
  - Scan files before execution if execution permission is required.

- Upload and Download Limits
  - Set proper file size limits for upload protection.
  - Consider post-decompression size limits for compressed files.
  - Implement request limits for download services to prevent DoS attacks.
  - Use secure methods to calculate ZIP file sizes safely.

- Additional Security Measures
  - Protect file upload endpoints from CSRF attacks.
  - Keep all file processing libraries securely configured and updated.
  - Implement logging and monitoring for upload activities.
  - Provide user reporting mechanisms for illegal content.
  - Use secure extraction methods for compressed files.

Summary:  
Implement defense-in-depth for file uploads through multi-layered validation, secure storage practices, proper access controls, and comprehensive monitoring. Never rely on single validation methods and always generate safe filenames to prevent attacks.
