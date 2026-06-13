# Week 2 Report: HockeyScrapper

**Team number:** 25

**Short description:** HockeyScrapper is a web platform that allows hockey fans to follow Kontinental Hockey League (KHL) teams and receive timely alerts about ticket sales.
Users can create an account, select their favourite teams and subscribe them. Once subscribed, the system automatically sends a notification as soon as ticket sales for a selected team's match begin. This ensures fans never miss the chance to buy tickets.

**Root LICENSE:** [`LICENSE`](../../LICENSE) — MIT

---

## 1. User Stories

[`reports/week2/user-stories.md`](user-stories.md)

---

## 2. Prototype and Interface Artifacts

**Interactive prototype (Figma):**
[HockeyScrapper Figma Prototype](https://www.figma.com/proto/QA9kxzUyxzBCnEycOYvinv/HockeyScrapper-Prototype?node-id=3-163&p=f&t=cW9lcLU0V8yCkDc5-1&scaling=scale-down&content-scaling=fixed&page-id=0%3A1&starting-point-node-id=3%3A163&show-proto-sidebar=1)

**Non-graphical interface (Telegram Bot):**
- Demonstration: [MVP v0 Video](https://www.youtube.com/watch?v=EXAMPLE)
- Documentation: [`docs/interface.md`](../../docs/interface.md)

---

## 3. MVP v0

- **Documentation:** [`reports/week2/mvp-v0-report.md`](mvp-v0-report.md)
- **Deployed MVP v0:** [https://hockeyscrapper-mvp-v0.onrender.com](https://hockeyscrapper-mvp-v0.onrender.com)
- **Run instructions:** See [root README.md](../../README.md) for local setup.

---

## 4. PR/MR Workflow

- **PR template:** [`.github/pull_request_template.md`](../../.github/pull_request_template.md)
- **Reviewed PRs:**
  - [PR #1: Add project setup files](https://github.com/kamillayarullina/hockeyscrapper/pull/1) (Example — replace with actual)
- **Branch protection:** Protected default branch (main) — see screenshot below.

![Protected default branch settings](images/branch-protection.png)
*Protected default branch settings — direct pushes disabled, PR approval required.*

![Example reviewed PR](images/reviewed-pr.png)
*Example of a reviewed PR — approval from another team member.*

---

## 5. Lychee Link Checking

- **Configuration:** [`.lychee.toml`](../../.lychee.toml)
- **CI workflow:** [`.github/workflows/lychee.yml`](../../.github/workflows/lychee.yml)
- **Latest successful run:** [Actions tab](https://github.com/kamillayarullina/hockeyscrapper/actions/workflows/lychee.yml)

### Excluded links

| Link | Reason for exclusion | Manually verified? |
|------|---------------------|--------------------|
| `https://github.com/*/issues/*` | Requires authentication | N/A — pattern |
| `https://github.com/*/pull/*` | Requires authentication | N/A — pattern |
| `https://www.figma.com/*` | Requires authentication | Yes |
| `http://localhost` | Local only | N/A |
| `http://127.0.0.1` | Local only | N/A |
| `https://my-mvp-v0.example.com` | Placeholder | No — replace with real URL |

---

## 6. Screenshots

### Protected default branch settings

![Protected default branch](images/branch-protection.png)

### Example reviewed PR/MR

![Reviewed PR](images/reviewed-pr.png)

### Selected prototype and interface artifacts

![Figma Prototype](images/prototype-screenshot.png)

### Deployed MVP v0

![MVP v0](images/mvp-v0-screenshot.png)

---

## 7. Coverage

### Prototype coverage

The Figma prototype covers the following user stories:

| Screen/Flow | User Stories |
|-------------|-------------|
| Registration & Login | US-01, US-02 |
| Team selection & subscription | US-03, US-04 |
| Match list view | US-05, US-07 |
| Notification settings | US-08 |
| Admin panel | US-10 |

### Interface artifacts coverage

The Telegram bot interface (documented in `docs/interface.md`) covers:

| Interface Element | User Stories |
|------------------|-------------|
| Subscribe command | US-03, US-04 |
| Unsubscribe command | US-03 |
| List subscriptions | US-06 |
| Match notifications | US-05, US-07 |
| Admin commands | US-10 |

### MVP v0 coverage

See [`reports/week2/mvp-v0-report.md`](mvp-v0-report.md) for the MVP v0 foundation details and smoke-check scenario. MVP v0 establishes the frontend hosting infrastructure and static page foundation, which supports the eventual implementation of US-01 (User registration) and US-02 (User login).

---

## 8. Customer Meeting

- **Transcript:** [`customer-meeting-transcript.md`](customer-meeting-transcript.md) (published with customer permission — see meeting summary)
- **Meeting summary:** [`customer-meeting-summary.md`](customer-meeting-summary.md)

---

## 9. Analysis

[`reports/week2/analysis.md`](analysis.md)

---

## 10. LLM Report

[`reports/week2/llm-report.md`](llm-report.md)
