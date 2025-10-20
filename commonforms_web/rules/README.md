# Project CodeGuard: Security Rules for AI Coding Agents
![Securing](https://img.shields.io/badge/Securing%20AI%20Generated%20Code-green)
![Open Source](https://img.shields.io/badge/Now-Open%20Source-brightgreen)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

This project is an AI model-agnostic security framework and ruleset (internally nicknamed "Project CodeGuard" when developed at Cisco) that embeds secure-by-default practices into AI coding workflows (generation and review). It ships core security rules, translators for popular coding agents, and validators to test rule compliance.


## Why Project CodeGuard?

AI coding agents are transforming software engineering, but this speed can introduce security vulnerabilities. Is your AI coding agent implementation introducing security vulnerabilities?

- ❌ Skipping input validation
- ❌ Hardcoding secrets and credentials
- ❌ Using weak cryptographic algorithms
- ❌ Relying on unsafe functions
- ❌ Missing authentication/authorization checks
- ❌ Missing any other security best practice

Project CodeGuard solves this by embedding security best practices directly into AI coding agent workflows. 

**During and After Code Generation.**

Project CodeGuard is designed to integrate seamlessly across the entire AI coding lifecycle. 
- **Before code generation**, rules can be used for the design of a product and for spec-driven development. You can use the rules in the “planning phase” of an AI coding agent to steer models toward secure patterns from the start.
- **During code generation**, rules can help AI agents to prevent security issues as code is being written.
- **After code generation**, AI agents like Cursor, GitHub Copilot, Codex, Windsurf, and Claude Code can use the rules for code review. 


## Security Coverage

Our rules cover essential security domains:

- **🔐 Cryptography**: Safe algorithms (including post-quantum cryptography), secure key management, certificate validation
- **🛡️ Input Validation**: SQL injection prevention, XSS protection, command injection defense
- **🔑 Authentication**: MFA best practices, OAuth/OIDC, secure session management
- **⚡ Authorization**: RBAC/ABAC, access control, IDOR prevention
- **📦 Supply Chain**: Dependency security, SBOM generation, vulnerability management
- **☁️ Cloud Security**: IaC hardening, container security, Kubernetes best practices
- **📱 Platform Security**: Mobile apps, web services, API security
- **🔍 Data Protection**: Privacy, encryption at rest/transit, secure storage

## Quick Start

Get started in minutes:

1. **Download the rules** from our [releases page](https://github.com/project-codeguard/rules/releases)
2. **Copy to your project** - Place AI agent and IDE specific rules in your repository
3. **Start coding** - AI assistants will automatically follow security best practices

- Additional details in the [Get Started →](getting-started.md)


## How It Works

1. **Security rules** are written in a unified markdown format
2. **Conversion tools** translate rules to IDE and AI agent formats
3. **AI assistants** reference these rules when generating or reviewing code
4. **Secure code** is produced automatically without developer intervention

## Community

- **📋 Issues**: [Report bugs or request features](https://github.com/project-codeguard/rules/issues)
- **💬 Discussions**: [Join the conversation](https://github.com/project-codeguard/rules/discussions)
- **🤝 Contributing**: [Learn how to contribute](https://github.com/project-codeguard/rules/blob/main/CONTRIBUTING.md)


## 📄 Licensing

This project uses dual licensing:

- **Security Rules & Documentation**: Licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/) - includes all rule files, documentation, and project content
- **Source Code & Tools**: The `src/` directory is licensed under [Apache License 2.0](src/LICENSE.md) - includes conversion tools, validators, and other software components

This licensing approach ensures the security rules remain freely accessible and reusable while providing appropriate terms for software components.


Copyright © 2025 Cisco Systems, Inc.