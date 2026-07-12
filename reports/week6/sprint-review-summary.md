# Week 6 Sprint Review and Customer Trial Summary

## Trial Outcome

The team demonstrated password-validation feedback, subscription management, mock checkout, paid-team management, and auto-renewal controls. Because the hosted build was inconsistent at the start of the meeting, parts of the trial were shown locally and parts on the staging host.

The customer positively evaluated the monetisation screens and the progress made during the week, but clarified that the initial three-free-team assumption was incorrect.

## Confirmed Monetisation Decisions

- The first team and every additional team require a separate subscription.
- The existing per-team model remains; it must not be replaced with one global Premium plan.
- The monthly plan costs 39 RUB.
- A yearly plan must be available for ten monthly prices: 390 RUB.
- No real YooKassa or YooMoney integration is required for the course version.
- Checkout must clearly state that no real money is charged, then create the subscription after the user confirms the mock payment.
- The existing paid-team management and per-team auto-renewal interface can remain as mock functionality.

## Transition Readiness

The customer did not consider the product ready for final transition yet. The critical remaining capability is reliable parsing of KHL club ticket pages and notifications when tickets become available. The customer said the product could be considered ready after that functionality is completed.

The customer had briefly used the product after the previous meeting but had not used it regularly. They planned to inspect the updated hosted version after the team deployed a stable build.

## Documentation Review

The team presented the repository README, startup instructions, testing documentation, architecture material, and the customer-handover document. No immediate documentation defect was reported during the meeting. The customer planned a later independent review of the updated repository and hosted product.

## Follow-up Actions

1. Implement the corrected mock monetisation rules and update tests and documentation.
2. Complete parser and ticket-availability notification work as the main Week 7 blocker.
3. Deploy a stable build and notify the customer when it is available for independent review.
4. Execute the revised monetisation UAT and final transition-readiness walkthrough.
