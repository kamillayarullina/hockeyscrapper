## QR-001: Critical module testability

**ISO/IEC 25010 sub-characteristic:** Testability

**Scenario:** When a developer changes a critical product module under the standard CI environment, the module shall have automated unit tests that achieve line coverage within 20% for that module.

**Why this matters:** Critical product logic must be directly verifiable so defects can be detected before merge.

**Linked quality requirement tests:** [QRT-001](quality-requirement-tests.md#qrt-001-critical-module-unit-coverage)

**Linked ADRs:** [ADR-001](architecture/adr/ADR-001-modular-parser-architecture.md) — modular parser architecture enables isolated unit testing of each parser subclass.

## QR-002: Security-lint feedback time

**ISO/IEC 25010 sub-characteristic:** Analysability

**Scenario:** When a developer opens or updates a pull request under the CI build environment, the product security-lint gate shall analyze the changed product code and complete within 30 seconds, failing the build if security issues are detected.

**Why this matters:** Developers need fast feedback about security mistakes so they can diagnose and fix vulnerabilities before merging.

**Linked quality requirement tests:** [QRT-002](quality-requirement-tests.md#qrt-002-ci-security-lint-feedback-time)

**Linked ADRs:** [ADR-002](architecture/adr/ADR-002-bcrypt-jwt-authentication.md) — authentication architecture defines security-sensitive code paths that security-lint gates target.

## QR-003: Password storage confidentiality

**ISO/IEC 25010 sub-characteristic:** Confidentiality

**Scenario:** When a user registers or changes a password under normal API operation, the system shall store the password only as a bcrypt hash and never in plaintext.

**Why this matters:** User passwords must be protected against credential disclosure in case of database compromise.

**Linked quality requirement tests:** [QRT-003](quality-requirement-tests.md#qrt-003-password-hash-confidentiality)

**Linked ADRs:** [ADR-002](architecture/adr/ADR-002-bcrypt-jwt-authentication.md) — bcrypt password hashing decision directly ensures password storage confidentiality.

## QR-004: Code maintainability тАФ ruff lint compliance

**ISO/IEC 25010 sub-characteristic:** Maintainability / Analysability

**Scenario:** When a developer runs `ruff check .` under the standard CI environment, all source files shall pass linting with zero errors. The CI build shall fail on any lint violation.

**Why this matters:** Consistent coding style and early detection of common defects reduce review overhead and improve code readability.

**Linked quality requirement tests:** [QRT-004](quality-requirement-tests.md#qrt-004-code-lint-compliance)

**Linked ADRs:** [ADR-001](architecture/adr/ADR-001-modular-parser-architecture.md) — consistent interface patterns across parser modules reduce lint noise and improve maintainability.

## QR-005: Startup reliability

**ISO/IEC 25010 sub-characteristic:** Reliability / Availability

**Scenario:** When the application starts via `main.py` under the standard test environment, all module imports shall succeed without error and the CLI argument parser shall respond correctly, confirming that initialization logic is free of syntax, import, and configuration errors.

**Why this matters:** A system that fails at startup is completely unusable. Verifying the import and initialization chain catches missing dependencies, broken imports, and configuration errors before deployment.

**Linked quality requirement tests:** [QRT-005](quality-requirement-tests.md#qrt-005-startup-import-integrity)

**Linked ADRs:** [ADR-003](architecture/adr/ADR-003-dual-service-deployment.md) — dual-service deployment isolates startup paths so each service validates its import chain independently.
