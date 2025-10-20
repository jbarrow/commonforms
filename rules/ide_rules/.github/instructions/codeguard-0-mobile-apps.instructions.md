---
applyTo: **/*.java,**/*.js,**/*.jsx,**/*.kt,**/*.kts,**/*.m,**/*.mjs,**/*.pl,**/*.pm,**/*.swift,**/*.wsdl,**/*.xml,**/*.xsd,**/*.xslt
title: 'Mobile app security (iOS/Android): storage, transport, code integrity, biometrics,
  permissions'
version: 1.0.0
---

rule_id: codeguard-0-mobile-apps

## Mobile Application Security Guidelines

Essential security practices for developing secure mobile applications across iOS and Android platforms.

### Architecture and Design

Implement secure design principles from the start:
- Follow least privilege and defense in depth principles
- Use standard secure authentication protocols (OAuth2, JWT)
- Perform all authentication and authorization checks server-side
- Request only necessary permissions for app and backend services
- Establish security controls for app updates, patches, and releases
- Use only trusted and validated third-party libraries and components

### Authentication and Authorization

Never trust the client for security decisions:
- Perform authentication/authorization server-side only
- Do not store user passwords on device; use revocable access tokens
- Avoid hardcoding credentials in the mobile app
- Encrypt credentials in transmission
- Use platform-specific secure storage (iOS Keychain, Android Keystore)
- Require password complexity and avoid short PINs (4 digits)
- Implement session timeouts and remote logout functionality
- Require re-authentication for sensitive operations
- Use platform-supported biometric authentication with secure fallbacks

### Data Storage and Privacy

Protect sensitive data at rest and in transit:
- Encrypt sensitive data using platform APIs; avoid custom encryption
- Leverage hardware-based security features (Secure Enclave, Strongbox)
- Store private data on device's internal storage only
- Minimize PII collection to necessity and implement automatic expiration
- Avoid caching, logging, or background snapshots of sensitive data
- Always use HTTPS for network communications

### Network Communication

Assume all network communication is insecure:
- Use HTTPS for all network communication
- Do not override SSL certificate validation for self-signed certificates
- Use strong, industry standard cipher suites with appropriate key lengths
- Use certificates signed by trusted CA providers
- Consider certificate pinning for additional security
- Encrypt data even if sent over SSL
- Avoid sending sensitive data via SMS

### Code Quality and Integrity

Maintain application security throughout development:
- Use static analysis tools to identify vulnerabilities
- Make security a focal point during code reviews
- Keep all libraries up to date to patch known vulnerabilities
- Disable debugging in production builds
- Include code to validate integrity of application code
- Obfuscate the app binary
- Implement runtime anti-tampering controls:
  - Check for debugging, hooking, or code injection
  - Detect emulator or rooted/jailbroken devices
  - Verify app signatures at runtime

### Platform-Specific Security

#### Android Security
- Use Android's ProGuard for code obfuscation
- Avoid storing sensitive data in SharedPreferences
- Disable backup mode to prevent sensitive data in backups
- Use Android Keystore with hardware backing (TEE or StrongBox)
- Implement Google's Play Integrity API for device and app integrity checks

#### iOS Security
- Configure Shortcuts permissions to require device unlock for sensitive actions
- Set Siri intent `requiresUserAuthentication` to true for sensitive functionality
- Implement authentication checks on deep link endpoints
- Use conditional logic to mask sensitive widget content on lock screen
- Store sensitive data in iOS Keychain, not plist files
- Use Secure Enclave for cryptographic key storage
- Implement App Attest API for app integrity validation
- Use DeviceCheck API for persistent device state tracking

### Testing and Monitoring

Validate security controls through comprehensive testing:
- Perform penetration testing including cryptographic vulnerability assessment
- Leverage automated tests to ensure security features work as expected
- Ensure security features do not harm usability
- Use real-time monitoring to detect and respond to threats
- Have a clear incident response plan in place
- Plan for regular updates and implement forced update mechanisms when necessary

### Input and Output Validation

Prevent injection and execution attacks:
- Validate and sanitize all user input
- Validate and sanitize output to prevent injection attacks
- Mask sensitive information on UI fields to prevent shoulder surfing
- Inform users about security-related activities (logins from new devices)

By following these practices derived from the OWASP Mobile Application Security framework, you can significantly improve the security posture of your mobile applications across both development and operational phases.
