# Definition of Done

## Mandatory Gates

These are required for every work item without exception:

- [ ] **All acceptance criteria are satisfied**
- [ ] **Reviewed by another team member**
- [ ] **Required tests or checks pass**
- [ ] **Verification evidence preserved**

---

## All Work Items

- [ ] Code compiles/parses without errors
- [ ] No secrets, tokens, or credentials committed
- [ ] No hardcoded configuration values that belong in `.env` or `config/sites.yaml`
- [ ] Changes are focused on a single concern
- [ ] Self-review completed before requesting peer review

---

## User Story (US)

- [ ] **Linked supporting PBI**
- [ ] Full flow works end-to-end from user perspective
- [ ] Bot commands (if applicable) respond with correct formatting
- [ ] Frontend pages (if applicable) render correctly and display data
- [ ] API endpoints (if applicable) return correct status codes and payloads
- [ ] Telegram notifications (if applicable) formatted and deduplicated correctly

---

## Technical PBI

- [ ] Implementation matches the architecture established in the codebase
- [ ] No unnecessary dependencies added to `requirements.txt`
- [ ] Async code uses proper await patterns (no blocking calls in async paths)
- [ ] Playwright/parser changes handle timeout and retry gracefully
- [ ] Proxy rotator changes maintain health-check compatibility
- [ ] for every user-visible change update CHANGELOG.md
---

## Bug Report

- [ ] Root cause identified and fixed
- [ ] Regression test added or manual test script documented
- [ ] The original bug scenario is verified as resolved