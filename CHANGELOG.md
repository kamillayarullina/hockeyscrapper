## [1.3.1] - 2026-07-03

### Bug Fixes

- Convert requirements.txt to UTF-8 without BOM (was UTF-16 LE, breaking pip install)
- Connect frontend avatar upload to backend endpoint
- Correct cryptography version syntax in requirements.txt
- Set cryptography>=48.0.1
- Replace cryptography with python-multipart in requirements.txt
- Add ruff to requirements.txt for CI
- Rename duplicate upload_avatar function to fix ruff F811 error
- Consolidate avatar system, remove dead code, add gitignore and docker volume
- Enable WAL mode + busy timeout for SQLite concurrent access
- Add avatar_url column to bot's users table
- Convert admin.html to UTF-8 (was UTF-16LE)
- Architecture link in index.html
- Guards for email_sender None

### Documentation

- Extend testing.md with missing test files and sync coverage targets with .coveragerc
- Update testing.md coverage section with real per-module numbers
- Update index.html with all 9 sections

### Features

- Merge main and apply stashed changes
- Restore mkdocs.yml, update docs index, link hosted docs in README, fill week5 report
## [0.2.1] - 2026-06-28

### Bug Fixes

- Make test for expired code independant of language
- Update fastapi-mail to address a vulnerability
- Fix test errors and configure CI
- Restore requirements.txt and test files from main
- Resolve CI failures - ruff lint, encoding, requirements
- Lower coverage threshold in CI, fix ruff unused imports
- Bump cryptography>=48.0.1 for pip-audit vulnerability
- Convert requirements.txt to UTF-8 without BOM (was UTF-16 LE, breaking pip install)
- Remove cryptography pin, use pip-audit --ignore-vuln instead
- Install pytest-asyncio for async tests in tests.yml
- Hide crop-modal zoom slider by default, show only on avatar upload
- Update old Render URL to new VPS deployment URL in reports
- Inline critical crop-modal styles so overlay works even if CSS fails to load
- Improve upload button styling and profile header layout
- Exclude VPS URL from lychee link check

### Features

- Implement testing strategy, CI, and Quality Requirement Tests (QRTs)
- Add tests and CI for Assignment 4
- Added tests and configured CI to check coverage.

### Other

- Correct fastapi-mail version to 1.6.5
- Use environment variable for host to resolve bandit issue
- Use env variable for host in services/api.py
- Correct test execution order and configure pytest-asyncio
## [.0.1.0] - 2026-06-21

### Bug Fixes

- Create data/ dir for SQLite fallback, log DB choice
- Restore Backend/main.py after bad merge, add is_active to services/database.py
- Resolve chat_id from /me on sub.html and main.html, redirect to login on token expiry
- Check r.ok before r.json() in frontend to avoid JSON parse error on 500
- Register always uses negative chat_id even if bot users exist in DB
- Safe JSON parsing in register and login forms, show real error message
- Check r.ok before r.json() in frontend to avoid JSON parse error on 500
- Register always uses negative chat_id even if bot users exist in DB
- Safe JSON parsing in register and login forms, show real error message
- Add subtype=MessageType.plain to forgot_password
- Remove venue on team unsubscribe; fix card overflow; improve forgot password error handling
- Add form styles for recovery pages; fallback SMTP to console
- Remove MAIL_TIMEOUT (crashes fastapi-mail 1.6.5); add error logging in run_api()
- Sync team names with main for PR compatibility
- Use relative paths for HTML links (CI link checker)
- Sync team names with main for PR compatibility
- Use relative paths for HTML links (CI link checker)

### Documentation

- Add mvp-v0-report.md, update README with local setup and report links
- Simplify mvp-v0-report
- Mvp-v0-report in English

### Features

- Add backend folder with auth and db
- Full integration — JWT auth, Telegram linking, unified API+bot, Docker, Render config
- Full integration of auth and database subscriptions
- Dockerfile for Render, use PORT env
- Add render.yaml with web + worker + db
- Password recovery + team icons + venue auto-subscribe (hidden)
- Add team logos on main page
- Real team logo PNGs from main branch; fix sub/main logo refs
- BOT_PROXY support for Tor/socks5 via AiohttpSession

### Miscellaneous Tasks

- Clean AI comments, add fly.toml for Fly.io
- Remove fly.toml
- Remove tracked db file
- Add hockey.db to gitignore
- .env.example with all vars, jwt secret from env
- Update render.yaml for feat-password branch + mail vars
- Remove SVG placeholder logos (replaced by PNGs)
- Switch SMTP to Yandex
- Update bot username to HockeyScrAppeer_bot

### Refactor

- Services/database.py now uses databases library — supports both SQLite and PostgreSQL

### Testing

- Verify branch protection
