# Lab Report #4

## Part 7: Automated Testing and Quality Assurance (QA)

A comprehensive testing and quality control system was built for the HockeyScrapper application as part of this section.

### 1. Testing Documentation

The entire testing strategy, architecture, coverage targets, and description of automated checks have been documented in the `docs/testing.md` file. This document serves as a single source of truth for how project quality is ensured.

### 2. Test Implementation

Several types of tests were implemented:

*   **Unit Tests**: These check isolated components of the system. For example, `tests/test_security.py` tests the correctness of password hashing and verification.
*   **Integration Tests**: `tests/test_api_integration.py` verifies the interaction between components via the API, emulating user actions (registration, login, password recovery).
*   **Quality Requirement Tests (QRTs)**: Three special tests were created to check non-functional requirements:
    *   **QRT-01 (Fault Tolerance)**: `tests/test_fault_tolerance.py` — ensures the parser correctly handles network errors (5xx) and performs retries without crashing.
    *   **QRT-02 (Confidentiality)**: `tests/test_auth_confidentiality.py` — guarantees that protected API endpoints return a 401 error on access attempts without a valid JWT token.
    *   **QRT-03 (Performance)**: `tests/test_notification_performance.py` — measures the speed of the notification engine under load to ensure it meets the performance limit.

### 3. Additional QA Check: Dependency Security Audit

An automatic check for known vulnerabilities in all third-party libraries from `requirements.txt` has been added to the CI pipeline. This uses the **`pip-audit`** tool, which queries the official PyPI vulnerability database.

**Objective**: To prevent supply-chain attacks, where a vulnerability in a used library could compromise the entire application.

If `pip-audit` finds a vulnerability, the project build is immediately halted, blocking the deployment of potentially insecure code.

## Part 8: CI (Continuous Integration) Setup

To automate all checks, a CI pipeline was configured using GitHub Actions. The configuration is located in the `.github/workflows/tests.yml` file.

The pipeline executes the following steps on every `push` or `pull request` to the `main` branch:

1.  **Checkout**: Downloads the latest version of the code from the repository.
2.  **Set up Python**: Installs the required Python version (3.11).
3.  **Install dependencies**: Installs all dependencies from `requirements.txt`.
4.  **Install Playwright**: Installs the browsers required for the parser to work.
5.  **Run `pip-audit`**: Executes the dependency security audit.
6.  **Run `Bandit`**: Runs the static analyzer to find security issues in the code.
7.  **Run tests with coverage**: Executes all tests (unit, integration, QRT) using `pytest` and collects the code coverage report.
8.  **Upload coverage report**: Uploads the coverage report as a build artifact for later analysis.

Thus, a full cycle of automatic quality and security code checking is ensured with every change.