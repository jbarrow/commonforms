---
applyTo: **/*.bash,**/*.c,**/*.ddl,**/*.dml,**/*.go,**/*.h,**/*.htm,**/*.html,**/*.java,**/*.js,**/*.jsx,**/*.mjs,**/*.php,**/*.ps1,**/*.py,**/*.pyi,**/*.pyx,**/*.rb,**/*.sh,**/*.sql,**/*.ts,**/*.tsx
title: Input validation and injection defense (SQL/LDAP/OS), parameterization, prototype
  pollution
version: 1.0.0
---

rule_id: codeguard-0-input-validation-injection

## Input Validation & Injection Defense

Ensure untrusted input is validated and never interpreted as code. Prevent injection across SQL, LDAP, OS commands, templating, and JavaScript runtime object graphs.

### Core Strategy
- Validate early at trust boundaries with positive (allow‑list) validation and canonicalization.
- Treat all untrusted input as data, never as code. Use safe APIs that separate code from data.
- Parameterize queries/commands; escape only as last resort and context‑specific.

### Validation Playbook
- Syntactic validation: enforce format, type, ranges, and lengths for each field.
- Semantic validation: enforce business rules (e.g., start ≤ end date, enum allow‑lists).
- Normalization: canonicalize encodings before validation; validate complete strings (regex anchors ^$); beware ReDoS.
- Free‑form text: define character class allow‑lists; normalize Unicode; set length bounds.
- Files: validate by content type (magic), size caps, and safe extensions; server‑generate filenames; scan; store outside web root.

### SQL Injection Prevention
- Use prepared statements and parameterized queries for 100% of data access.
- Use bind variables for any dynamic SQL construction within stored procedures and never concatenate user input into SQL.
- Prefer least‑privilege DB users and views; never grant admin to app accounts.
- Escaping is fragile and discouraged; parameterization is the primary defense.

Example (Java PreparedStatement):
```java
String custname = request.getParameter("customerName");
String query = "SELECT account_balance FROM user_data WHERE user_name = ? ";  
PreparedStatement pstmt = connection.prepareStatement( query );
pstmt.setString( 1, custname);
ResultSet results = pstmt.executeQuery( );
```

### LDAP Injection Prevention
- Always apply context‑appropriate escaping:
  - DN escaping for `\ # + < > , ; " =` and leading/trailing spaces
  - Filter escaping for `* ( ) \ NUL`
- Validate inputs with allow‑lists before constructing queries; use libraries that provide DN/filter encoders.
- Use least‑privilege LDAP connections with bind authentication; avoid anonymous binds for application queries.

### OS Command Injection Defense
- Prefer built‑in APIs instead of shelling out (e.g., library calls over `exec`).
- If unavoidable, use structured execution that separates command and arguments (e.g., ProcessBuilder). Do not invoke shells.
- Strictly allow‑list commands and validate arguments with allow‑list regex; exclude metacharacters (& | ; $ > < ` \ ! ' " ( ) and whitespace as needed).
- Use `--` to delimit arguments where supported to prevent option injection.

Example (Java ProcessBuilder):
```java
ProcessBuilder pb = new ProcessBuilder("TrustedCmd", "Arg1", "Arg2");
Map<String,String> env = pb.environment();
pb.directory(new File("TrustedDir"));
Process p = pb.start();
```

### Query Parameterization Guidance
- Use the platform’s parameterization features (JDBC PreparedStatement, .NET SqlCommand, Ruby ActiveRecord bind params, PHP PDO, SQLx bind, etc.).
- For stored procedures, ensure parameters are bound; never build dynamic SQL via string concatenation inside procedures.

### Prototype Pollution (JavaScript)
- Developers should use `new Set()` or `new Map()` instead of using object literals
- When objects are required, create with `Object.create(null)` or `{ __proto__: null }` to avoid inherited prototypes.
- Freeze or seal objects that should be immutable; consider Node `--disable-proto=delete` as defense‑in‑depth.
- Avoid unsafe deep merge utilities; validate keys against allow‑lists and block `__proto__`, `constructor`, `prototype`.

### Caching and Transport
- Apply `Cache-Control: no-store` on responses containing sensitive data; enforce HTTPS across data flows.

### Implementation Checklist
- Central validators: types, ranges, lengths, enums; canonicalization before checks.
- 100% parameterization coverage for SQL; dynamic identifiers via allow‑lists only.
- LDAP DN/filter escaping in use; inputs validated prior to query.
- No shell invocation for untrusted input; if unavoidable, structured exec + allow‑list + regex validation.
- JS object graph hardened: safe constructors, blocked prototype paths, safe merge utilities.
- File uploads validated by content, size, and extension; stored outside web root and scanned.

### Test Plan
- Static checks for string concatenation in queries/commands and dangerous DOM/merge sinks.
- Fuzzing for SQL/LDAP/OS injection vectors; unit tests for validator edge cases.
- Negative tests exercising blocked prototype keys and deep merge behavior.
