# Quality Requirement Tests (QRTs)

## What counts as an automated QRT

A quality requirement test (QRT) is an automated test or CI check that directly verifies one or more measurable quality requirement scenarios. The following evidence types may count as QRTs under these conditions:

| Evidence type | Counts as QRT? | Condition |
|---|---|---|
| **CI job/check** (e.g., coverage gate, linter gate) | Yes | Directly verifies a measurable QR scenario. The automated command is defined in the CI workflow and its result is captured in CI run logs. |
| **Unit test** (pytest file in `tests/`) | Yes | Only if directly linked to a measurable QR scenario and verifying its response measure. |
| **Integration test** (pytest file in `tests/`) | Yes | Only if directly linked to a measurable QR scenario. |
| **Coverage measurement** | Yes | Only when a coverage threshold (`fail_under`) is enforced as an automated gate. |
| **Static analysis / security lint** | Yes | Only when the tool exits non-zero on findings, making it a gating check. |
| **Type checking** | Not applicable | Not used in this project. |
| **User acceptance test (UAT)** | No | Manual or customer-executed scenarios do not qualify as automated QRTs. |
| **Manual evidence** (review, screenshot, observation) | No | Manual checks are not automated and do not count as QRTs. |

## Required fields

Each QRT entry must define:

- **Stable ID** (`QRT-NNN`)
- **Linked quality requirement** (`QR-NNN`)
- **Verification method** — automated CI check, unit test, integration test, or static analysis
- **Test data, setup, or environment**
- **Automated command or CI check**
- **Expected measurable result**
- **Evidence location** — where the result is captured (test file path, CI job name, CI run URL)

---

## QRT-001: Critical module unit coverage

**Linked quality requirement:** QR-001

**Verification method:** Automated CI check (coverage gate) + repository test.

**Test data, setup, or environment:** Standard CI build environment for pull requests and protected default-branch updates.

**Automated command or CI check:** `pytest tests/test_qrt_coverage.py tests/test_qrt_bandit.py -v`

**Expected measurable result:**
- Each critical module (`Backend/security.py`, `Backend/jwt_auth.py`) has automated unit tests that achieve at least 20% line coverage.
- The QRT test `test_qrt_coverage.py` validates that if `fail_under` is set in `.coveragerc`, it is at least 20.

**Repository test location:** `tests/test_qrt_coverage.py` — validates `.coveragerc` exists, `fail_under` is set >= 80, and `Backend` + `services` are in the source list.

**CI evidence location:** `.github/workflows/tests.yml` — step "Run unit and integration tests with coverage".

**Evidence link:** Latest protected default-branch CI run showing coverage summary and exit code.

---

## QRT-002: CI security-lint feedback time

**Linked quality requirement:** QR-002

**Verification method:** Automated CI check (security-lint gate) + repository test.

**Test data, setup, or environment:** Standard CI build environment for pull requests and protected default-branch updates.

**Automated command or CI check:** `bandit -c pyproject.toml -r Backend services -f txt`

**Expected measurable result:**
- The bandit gate completes in 30 seconds or less.
- The gate exits non-zero when security issues are detected, failing the build (no `|| true` suppression).

**Repository test location:** `tests/test_qrt_bandit.py` — validates `[tool.bandit]` exists in `pyproject.toml` and bandit runs successfully within 30-second timeout.

**CI evidence location:** `.github/workflows/tests.yml` — step "Additional QA check — Bandit (security lint)".

**Evidence link:** Latest protected default-branch CI run showing the job result and duration.

---

## QRT-003: Password hash confidentiality

**Linked quality requirement:** QR-003

**Verification method:** Automated unit tests.

**Test data, setup, or environment:** Standard test environment with pytest.

**Automated command or CI check:** `pytest tests/test_security.py -v`

**Expected measurable result:** All tests in `tests/test_security.py` pass. Specifically:
- `test_starts_with_bcrypt_prefix` — verifies hash starts with `$2b$`
- `test_different_salts` — verifies each hash is uniquely salted
- `test_correct_password` — verifies `verify_password` matches correct password
- `test_incorrect_password` — verifies `verify_password` rejects wrong password

These tests confirm that passwords are stored only as bcrypt hashes and never in plaintext.

**Repository test location:** `tests/test_security.py`

**CI evidence location:** `.github/workflows/tests.yml` — step "Run unit and integration tests with coverage" (included in the full test suite).

**Evidence link:** Latest protected default-branch CI run showing test results.
