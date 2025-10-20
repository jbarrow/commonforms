---
applyTo: **/*.c,**/*.go,**/*.h,**/*.java,**/*.js,**/*.jsx,**/*.mjs,**/*.php,**/*.py,**/*.pyi,**/*.pyx,**/*.rb,**/*.ts,**/*.tsx,**/*.yaml,**/*.yml
title: Authorization and access control (RBAC/ABAC/ReBAC, IDOR, mass assignment, transaction
  auth)
version: 1.0.0
---

rule_id: codeguard-0-authorization-access-control

## Authorization & Access Control

Enforce least privilege and precise access decisions for every request and resource, prevent IDOR and mass assignment, and provide strong transaction authorization where necessary.

### Core Principles
1.  Deny by Default: The default for any access request should be 'deny'. Explicitly grant permissions to roles or users rather than explicitly denying them. When no allow rule matches, return HTTP 403 Forbidden.
2.  Principle of Least Privilege: Grant users the minimum level of access required to perform their job functions. Regularly audit permissions to ensure they are not excessive.
3.  Validate Permissions on Every Request: Check authorization for every single request, regardless of source (AJAX, API, direct). Use middleware/filters to ensure consistent enforcement.
4.  Prefer ABAC/ReBAC over RBAC: Use Attribute-Based Access Control (ABAC) or Relationship-Based Access Control (ReBAC) for fine-grained permissions instead of simple role-based access control.

### Systemic Controls
- Centralize authorization at service boundaries via middleware/policies/filters.
- Model permissions at the resource level (ownership/tenancy) and enforce scoping in data queries.
- Return generic 403/404 responses to avoid leaking resource existence.
- Log all denials with user, action, resource identifier (non-PII), and rationale code.

### Preventing IDOR
- Never trust user-supplied identifiers alone. Always verify access to each object instance.
- Resolve resources through user-scoped queries or server-side lookups. Example: `currentUser.projects.find(id)` instead of `Project.find(id)`.
- Use non-enumerable identifiers (UUIDs/random) as defense-in-depth. Do not rely on obscurity alone.

### Preventing Mass Assignment
- Do not bind request bodies directly to domain objects containing sensitive fields.
- Expose only safe, editable fields via DTOs. Maintain explicit allow-lists for patch/update.
- Use framework features to block-list sensitive fields if allow-listing is infeasible.

### Transaction Authorization (Step-Up)
- Require a second factor for sensitive actions (wire transfers, privilege elevation, data export). Apply What‑You‑See‑Is‑What‑You‑Sign: show critical fields for user confirmation.
- Use unique, time‑limited authorization credentials per transaction; reject on data changes mid‑flow.
- Enforce the chosen authorization method server-side; prevent client‑side downgrades.
- Protect against brute-force with throttling and complete flow restarts after failures.

### Testing and Automation
- Maintain an authorization matrix (YAML/JSON) listing endpoints/resources, roles/attributes, and expected outcomes.
- Automate integration tests that iterate the matrix, mint role tokens, and assert allow/deny results—including token expiry/revocation cases.
- Exercise negative tests: swapped IDs, downgraded roles, missing scopes, and bypass attempts.

### Implementation Checklist
- Middleware/policies enforce deny-by-default and resource checks on every endpoint.
- Query scoping ensures users only access permitted rows/objects.
- DTOs and allow-lists prevent mass assignment; sensitive fields never bindable.
- Step-up authorization in place for sensitive operations with unique, short-lived credentials.
- Authorization matrix drives CI tests; failures block merges.
