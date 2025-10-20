---
applyTo: **/*.c,**/*.h,**/*.java,**/*.js,**/*.jsx,**/*.kt,**/*.kts,**/*.mjs,**/*.php,**/*.py,**/*.pyi,**/*.pyx,**/*.rb,**/*.ts,**/*.tsx,**/*.wsdl,**/*.xml,**/*.xsd,**/*.xslt,**/*.yaml,**/*.yml
title: Framework & language security guides (Django/DRF, Laravel/Symfony/Rails, .NET,
  Java/JAAS, Node.js, PHP config)
version: 1.0.0
---

rule_id: codeguard-0-framework-and-languages

## Framework & Language Guides

Apply secure‑by‑default patterns per platform. Harden configurations, use built‑in protections, and avoid common pitfalls.

### Django
- Disable DEBUG in production; keep Django and deps updated.
- Enable `SecurityMiddleware`, clickjacking middleware, MIME sniffing protection.
- Force HTTPS (`SECURE_SSL_REDIRECT`); configure HSTS; set secure cookie flags (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`).
- CSRF: ensure `CsrfViewMiddleware` and `{% csrf_token %}` in forms; proper AJAX token handling.
- XSS: rely on template auto‑escaping; avoid `mark_safe` unless trusted; use `json_script` for JS.
- Auth: use `django.contrib.auth`; validators in `AUTH_PASSWORD_VALIDATORS`.
- Secrets: generate via `get_random_secret_key`; store in env/secrets manager.

### Django REST Framework (DRF)
- Set `DEFAULT_AUTHENTICATION_CLASSES` and restrictive `DEFAULT_PERMISSION_CLASSES`; never leave `AllowAny` for protected endpoints.
- Always call `self.check_object_permissions(request, obj)` for object‑level authz.
- Serializers: explicit `fields=[...]`; avoid `exclude` and `"__all__"`.
- Throttling: enable rate limits (and/or at gateway/WAF).
- Disable unsafe HTTP methods where not needed. Avoid raw SQL; use ORM/parameters.

### Laravel
- Production: `APP_DEBUG=false`; generate app key; secure file perms.
- Cookies/sessions: enable encryption middleware; set `http_only`, `same_site`, `secure`, short lifetimes.
- Mass assignment: use `$request->only()` / `$request->validated()`; avoid `$request->all()`.
- SQLi: use Eloquent parameterization; validate dynamic identifiers.
- XSS: rely on Blade escaping; avoid `{!! ... !!}` for untrusted data.
- File uploads: validate `file`, size, and `mimes`; sanitize filenames with `basename`.
- CSRF: ensure middleware and form tokens enabled.

### Symfony
- XSS: Twig auto‑escaping; avoid `|raw` unless trusted.
- CSRF: use `csrf_token()` and `isCsrfTokenValid()` for manual flows; Forms include tokens by default.
- SQLi: Doctrine parameterized queries; never concatenate inputs.
- Command execution: avoid `exec/shell_exec`; use Filesystem component.
- Uploads: validate with `#[File(...)]`; store outside public; unique names.
- Directory traversal: validate `realpath`/`basename` and enforce allowed roots.
- Sessions/security: configure secure cookies and authentication providers/firewalls.

### Ruby on Rails
- Avoid dangerous functions:

```ruby
eval("ruby code here")
system("os command here")
`ls -al /` # (backticks contain os command)
exec("os command here")
spawn("os command here")
open("| os command here")
Process.exec("os command here")
Process.spawn("os command here")
IO.binread("| os command here")
IO.binwrite("| os command here", "foo")
IO.foreach("| os command here") {}
IO.popen("os command here")
IO.read("| os command here")
IO.readlines("| os command here")
IO.write("| os command here", "foo")
```

- SQLi: always parameterize; use `sanitize_sql_like` for LIKE patterns.
- XSS: default auto‑escape; avoid `raw`, `html_safe` on untrusted data; use `sanitize` allow‑lists.
- Sessions: database‑backed store for sensitive apps; force HTTPS (`config.force_ssl = true`).
- Auth: use Devise or proven libraries; configure routes and protected areas.
- CSRF: `protect_from_forgery` for state‑changing actions.
- Secure redirects: validate/allow‑list targets.
- Headers/CORS: set secure defaults; configure `rack-cors` carefully.

### .NET (ASP.NET Core)
- Keep runtime and NuGet packages updated; enable SCA in CI.
- Authz: use `[Authorize]` attributes; perform server‑side checks; prevent IDOR.
- Authn/sessions: ASP.NET Identity; lockouts; cookies `HttpOnly`/`Secure`; short timeouts.
- Crypto: use PBKDF2 for passwords, AES‑GCM for encryption; DPAPI for local secrets; TLS 1.2+.
- Injection: parameterize SQL/LDAP; validate with allow‑lists.
- Config: enforce HTTPS redirects; remove version headers; set CSP/HSTS/X‑Content‑Type‑Options.
- CSRF: anti‑forgery tokens on state‑changing actions; validate on server.

### Java and JAAS
- SQL/JPA: use `PreparedStatement`/named parameters; never concatenate input.
- XSS: allow‑list validation; sanitize output with reputable libs; encode for context.
- Logging: parameterized logging to prevent log injection.
- Crypto: AES‑GCM; secure random nonces; never hardcode keys; use KMS/HSM.
- JAAS: configure `LoginModule` stanzas; implement `initialize/login/commit/abort/logout`; avoid exposing credentials; segregate public/private credentials; manage subject principals properly.

### Node.js
- Limit request sizes; validate and sanitize input; escape output.
- Avoid `eval`, `child_process.exec` with user input; use `helmet` for headers; `hpp` for parameter pollution.
- Rate limit auth endpoints; monitor event loop health; handle uncaught exceptions cleanly.
- Cookies: set `secure`, `httpOnly`, `sameSite`; set `NODE_ENV=production`.
- Keep packages updated; run `npm audit`; use security linters and ReDoS testing.

### PHP Configuration
- Production php.ini: `expose_php=Off`, log errors not display; restrict `allow_url_fopen/include`; set `open_basedir`.
- Disable dangerous functions; set session cookie flags (`Secure`, `HttpOnly`, `SameSite=Strict`); enable strict session mode.
- Constrain upload size/number; set resource limits (memory, post size, execution time).
- Use Snuffleupagus or similar for additional hardening.

### Implementation Checklist
- Use each framework’s built‑in CSRF/XSS/session protections and secure cookie flags.
- Parameterize all data access; avoid dangerous OS/exec functions with untrusted input.
- Enforce HTTPS/HSTS; set secure headers.
- Centralize secret management; never hardcode secrets; lock down debug in production.
- Validate/allow‑list redirects and dynamic identifiers.
- Keep dependencies and frameworks updated; run SCA and static analysis regularly.
