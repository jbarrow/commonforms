---
trigger: glob
globs: **/*.c,**/*.h,**/*.htm,**/*.html,**/*.js,**/*.jsx,**/*.mjs,**/*.php,**/*.ts,**/*.tsx,**/*.v
title: Client-side web security (XSS/DOM XSS, CSP, CSRF, clickjacking, XS-Leaks, third-party
  JS)
version: 1.0.0
---

rule_id: codeguard-0-client-side-web-security

## Client‑side Web Security

Protect browser clients against code injection, request forgery, UI redress, cross‑site leaks, and unsafe third‑party scripts with layered, context‑aware controls.

### XSS Prevention (Context‑Aware)
- HTML context: prefer `textContent`. If HTML is required, sanitize with a vetted library (e.g., DOMPurify) and strict allow‑lists.
- Attribute context: always quote attributes and encode values.
- JavaScript context: do not build JS from untrusted strings; avoid inline event handlers; use `addEventListener`.
- URL context: validate protocol/domain and encode; block `javascript:` and data URLs where inappropriate.
- Redirects/forwards: never use user input directly for destinations; use server-side mapping (ID→URL) or validate against trusted domain allowlists.
- CSS context: allow‑list values; never inject raw style text from users.

Example sanitization:
```javascript
const clean = DOMPurify.sanitize(userHtml, {
  ALLOWED_TAGS: ['b','i','p','a','ul','li'],
  ALLOWED_ATTR: ['href','target','rel'],
  ALLOW_DATA_ATTR: false
});
```

### DOM‑based XSS and Dangerous Sinks
- Prohibit `innerHTML`, `outerHTML`, `document.write` with untrusted data.
- Prohibit `eval`, `new Function`, string‑based `setTimeout/Interval`.
- Validate and encode data before assigning to `location` or event handler properties.
- Use strict mode and explicit variable declarations to prevent global namespace pollution from DOM clobbering.
- Adopt Trusted Types and enforce strict CSP to prevent DOM sinks exploitation.

Trusted Types + CSP:
```http
Content-Security-Policy: script-src 'self' 'nonce-{random}'; object-src 'none'; base-uri 'self'; require-trusted-types-for 'script'
```

### Content Security Policy (CSP)
- Prefer nonce‑based or hash‑based CSP over domain allow‑lists.
- Start with Report‑Only mode; collect violations; then enforce.
- Baseline to aim for: `default-src 'self'; style-src 'self' 'unsafe-inline'; frame-ancestors 'self'; form-action 'self'; object-src 'none'; base-uri 'none'; upgrade-insecure-requests`.

### CSRF Defense
- Fix XSS first; then layer CSRF defenses.
- Use framework‑native CSRF protections and synchronizer tokens on all state‑changing requests.
- Cookie settings: `SameSite=Lax` or `Strict`; sessions `Secure` and `HttpOnly`; use `__Host-` prefix when possible.
- Validate Origin/Referer; require custom headers for API mutations in SPA token models.
- Never use GET for state changes; validate tokens on POST/PUT/DELETE/PATCH only. Enforce HTTPS for all token transmission.

### Clickjacking Defense
- Primary: `Content-Security-Policy: frame-ancestors 'none'` or a specific allow‑list.
- Fallback for legacy browsers: `X-Frame-Options: DENY` or `SAMEORIGIN`.
- Consider UX confirmations for sensitive actions when framing is required.

### Cross‑Site Leaks (XS‑Leaks) Controls
- Use `SameSite` cookies appropriately; prefer `Strict` for sensitive actions.
- Adopt Fetch Metadata protections to block suspicious cross‑site requests.
- Isolate browsing contexts: COOP/COEP and CORP where applicable.
- Disable caching and add user‑unique tokens for sensitive responses to prevent cache probing.

### Third‑Party JavaScript
- Minimize and isolate: prefer sandboxed iframes with `sandbox` and postMessage origin checks.
- Use Subresource Integrity (SRI) for external scripts and monitor for changes.
- Provide a first‑party, sanitized data layer; deny direct DOM access from tags where possible.
- Govern via tag manager controls and vendor contracts; keep libraries updated.

SRI example:
```html
<script src="https://cdn.vendor.com/app.js"
  integrity="sha384-..." crossorigin="anonymous"></script>
```

### HTML5, CORS, WebSockets, Storage
- postMessage: always specify exact target origin; verify `event.origin` on receive.
- CORS: avoid `*`; allow‑list origins; validate preflights; do not rely on CORS for authz.
- WebSockets: require `wss://`, origin checks, auth, message size limits, and safe JSON parsing.
- Client storage: never store secrets in `localStorage`/`sessionStorage`; prefer HttpOnly cookies; if unavoidable, isolate via Web Workers.
- Links: add `rel="noopener noreferrer"` to external `target=_blank` links.

### HTTP Security Headers (Client Impact)
- HSTS: enforce HTTPS everywhere.
- X‑Content‑Type‑Options: `nosniff`.
- Referrer‑Policy and Permissions‑Policy: restrict sensitive signals and capabilities.

### AJAX and Safe DOM APIs
- Avoid dynamic code execution; use function callbacks, not strings.
- Build JSON with `JSON.stringify`; never via string concatenation.
- Prefer creating elements and setting `textContent`/safe attributes over raw HTML insertion.

### Implementation Checklist
- Contextual encoding/sanitization for every sink; no dangerous APIs without guards.
- Strict CSP with nonces and Trusted Types; violations monitored.
- CSRF tokens on all state‑changing requests; secure cookie attributes.
- Frame protections set; XS‑Leak mitigations enabled (Fetch Metadata, COOP/COEP/CORP).
- Third‑party JS isolated with SRI and sandbox; vetted data layer only.
- HTML5/CORS/WebSocket usage hardened; no secrets in web storage.
- Security headers enabled and validated.

### Test Plan
- Automated checks for dangerous DOM/API patterns.
- E2E tests for CSRF and clickjacking; CSP report monitoring.
- Manual probes for XS‑Leaks (frame count, timing, cache) and open redirect behavior.
