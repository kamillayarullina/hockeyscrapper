## QR-001: Critical module testability

**ISO/IEC 25010 sub-characteristic:** Testability

**Scenario:** When a developer changes a critical product module under the standard CI environment, the module shall have automated unit tests that achieve line coverage within 80% for that module.

**Why this matters:** Critical product logic must be directly verifiable so defects can be detected before merge.

**Linked quality requirement tests:** [QRT-001](quality-requirement-tests.md#qrt-001-critical-module-unit-coverage)

## QR-002: Security-lint feedback time

**ISO/IEC 25010 sub-characteristic:** Analysability

**Scenario:** When a developer opens or updates a pull request under the CI build environment, the product security-lint gate shall analyze the changed product code and complete within 30 seconds, failing the build if security issues are detected.

**Why this matters:** Developers need fast feedback about security mistakes so they can diagnose and fix vulnerabilities before merging.

**Linked quality requirement tests:** [QRT-002](quality-requirement-tests.md#qrt-002-ci-security-lint-feedback-time)

## QR-003: Password storage confidentiality

**ISO/IEC 25010 sub-characteristic:** Confidentiality

**Scenario:** When a user registers or changes a password under normal API operation, the system shall store the password only as a bcrypt hash and never in plaintext.

**Why this matters:** User passwords must be protected against credential disclosure in case of database compromise.

**Linked quality requirement tests:** [QRT-003](quality-requirement-tests.md#qrt-003-password-hash-confidentiality)
