# Week 2 Report: HockeyScrapper

**Team number:** 25

## 1. **Short description:** HockeyScrapper is a web platform that allows hockey fans to follow Kontinental Hockey League (KHL) teams and receive timely alerts about ticket sales.
Users can create an account, select their favourite teams and subscribe them. Once subscribed, the system automatically sends a notification as soon as ticket sales for a selected team's match begin. This ensures fans never miss the chance to buy tickets.

**Root LICENSE:** [`LICENSE`](../../LICENSE) — MIT

---

## 2. User Stories

[`reports/week2/user-stories.md`](user-stories.md)

---

## 3. Prototype and Interface Artifacts

**Interactive prototype (Figma):**
[HockeyScrapper Figma Prototype](https://www.figma.com/proto/QA9kxzUyxzBCnEycOYvinv/HockeyScrapper-Prototype?node-id=3-163&p=f&t=cW9lcLU0V8yCkDc5-1&scaling=scale-down&content-scaling=fixed&page-id=0%3A1&starting-point-node-id=3%3A163&show-proto-sidebar=1)

**Non-graphical interface (Telegram Bot):**
- Demonstration: [Telegram bot demo](https://drive.google.com/drive/folders/1KM8mjVmRVEtvAi60wAL4QUFikZs4Hz5z?usp=share_link)
- Documentation: [`docs/interface.md`](../../docs/interface.md)

---

## 4. MVP v0

- **Documentation:** [`reports/week2/mvp-v0-report.md`](mvp-v0-report.md)
- **Deployed MVP v0:** *(будет добавлено)*
- **Run instructions:** See [root README.md](../../README.md) for local setup.

---

## 5. PR/MR Workflow

- **PR template:** [`.github/pull_request_template.md`](../../.github/pull_request_template.md)
- **Reviewed PRs:**
  - [PR #1: Add project setup files]
- **Branch protection:** Protected default branch (main) — see screenshot below.


*Protected default branch settings — direct pushes disabled, PR approval required.*


*Example of a reviewed PR — approval from another team member.*

---

## 6-7. Lychee Link Checking

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
| `https://my-mvp-v0.example.com` | Placeholder | No — удалён из README |
| `https://ticket-hockey.ru/*` | Example domain in docs | No — удалён из docs/interface.md |
| Root-relative paths в Frontend HTML | Исправлены на относительные | Да |
| `https://googleapis.com` | Typo | No — удалён из index.html |

---

## 8. Screenshots

### Protected default branch settings

![Protected default branch settings](images/Ruleset.png)

### Example reviewed PR/MR

![Example reviewed PR](images/PR.png)
![Example reviewed PR](images/PR2.png)

### Selected prototype and interface artifacts
![Prototype of main screen](images/Mainscreen.png)
![Prototype of main screen](images/Mainscreen2.png)
![Prototype of main screen](images/Mainscreen3.png)
![Prototype of registration screen](images/Register.png)
![Prototype of registration screen](images/Registererr.png)
![Prototype of login screen](images/Login.png)
![Prototype of profile screen](images/Profileuser.png)
![Prototype of subscriptions screen](images/Subscriptions.png)

### Deployed MVP v0



---

## 9. Coverage

### Prototype coverage

The Figma prototype covers the following user stories:

| Screen/Flow | User Stories |
|-------------|-------------|
| Profile | US-07 |
| Team selection and subscription | US-01, US-04 |


### Interface artifacts coverage

The Telegram bot interface (documented in `docs/interface.md`) covers:

| Interface Element | User Stories |
|------------------|-------------|
| Subscribe command | US-01 |
| Teams command | US-04 |
| Match command | US-02, US-03 |
| Match notifications | US-05 |
| Admin commands | US-11 |

### Selected prototype and interface artifacts
We chose an **interactive Figma prototype** because it allows the customer to validate the user flow without backend implementation.  
The following artifacts are provided:

- **Figma prototype** – demonstrates US‑01, US‑04, US‑07 (team subscription, list of KHL teams, profile view with subscriptions).
- **Telegram bot** – demonstrates US‑01, US-02, US-03, US-04, US-05, US-11 (team subscription, date and time of the match, ticket price, list of KHL teams, notifications getting, websites parsing(only admin access)).


### MVP v0 coverage

See [`reports/week2/mvp-v0-report.md`](mvp-v0-report.md) for the MVP v0 foundation details and smoke-check scenario. MVP v0 establishes the frontend hosting infrastructure and static page foundation, which supports the eventual implementation of US-01 (User registration) and US-02 (User login).

### User stories represented by MVP v0 (foundation only)
- **US‑01** – user can subscribe a team using telegram bot.
- **US‑02** – user can view date and time of the match using telegram bot.
- **US‑03** – user can view ticket price using telegram bot.
- **US‑04** – user can view list of KHL teams using telegram bot.
- **US‑05** – user can get notifications about match through telegram bot.
- **US‑11** – admin can edit parsing time through admin panel in telegram bot.

---

## 10-11. Customer Meeting

- **Transcript:** [`customer-meeting-transcript.md`](customer-meeting-transcript.md) (published with customer permission — see meeting summary)
- **Meeting summary:** [`customer-meeting-summary.md`](customer-meeting-summary.md)

---

## 12. Analysis

[`reports/week2/analysis.md`](analysis.md)

---

## 13. LLM Report

[`reports/week2/llm-report.md`](llm-report.md)
