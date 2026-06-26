# Week 4 Reflection

### Customer review

будет написано

### Release preparation

The team completed performance stabilization and debugging, significantly improving the product's speed and reliability. 

---

## Validated assumptions

| Assumption | Validation | Verdict |
|---|---|---|
| Telegram alias validation is a quick fix | Implemented | ✅ Confirmed |
| Admin panel can be built and deployed as a standalone page | Implemented | ✅ Confirmed |
| Performance stabilization can be done in one Sprint | Implemented | ✅ Confirmed |
| Password must contain only letters and numbers | This addition makes the password less secure| ❌ Rejected|

---

## Friction and gaps

### Unresolved requirements
- **Email notification** (part of US-05): Not implemented. Customer did not emphasise it, but it remains in the backlog.
- **Monetisation** (US-06): Not started. MoSCoW "Must have" — deferred to post-MVP.
- **Number of subscriptions** (US-09): Not started. MoSCoW "Could have".

### Technical risks
- **Parser on Yandex.Afisha (World Cup tickets)**: Untested. Captcha and rate-limiting may block scraping. High risk for production.
- **Proxy reliability**: Code is in place but no production test has been run.

### Missing scope
- Load testing not performed.

### Follow-up questions
- How will the parser handle captcha on Yandex.Afisha?

### Uncertainties
- Whether the parser can sustain high-frequency scraping against Yandex.Afisha anti-bot measures is unknown until tested.

---

## Planned response

сделаю после интервью
