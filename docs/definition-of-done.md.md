# Definition of Done (DoD)

**Version:** 2.0
**Last Updated:** 2026-06-20
**Applies to:** All User Stories, Tasks, and Bug Fixes for the [Product Name] Project.

## Purpose
The Definition of Done is a shared and formal commitment that ensures every completed work item meets our quality standards. It provides complete transparency for the team and stakeholders on what "done" truly means. A Product Backlog item is only considered "done" if it fulfills every criterion listed below.

## Core Quality Standards

For a user story, task, or bug to be marked as **Done**, it MUST meet **ALL** of the following criteria:

### 1. Code Implementation
- [ ] **Code is Written:** All required code, database migrations, and configuration changes are complete.
- [ ] **Coding Standards:** Code follows the team's established style guide and best practices.
- [ ] **Self-Reviewed:** The developer has performed a self-review to check for obvious errors, code smells, and debugging statements.
- [ ] **Peer-Reviewed:** The code has passed a formal code review by at least one other team member.
- [ ] **No Technical Debt:** No `TODO` comments or intentional shortcuts have been introduced without a separate task to address them.
- [ ] **Accessibility:** Code meets basic accessibility standards (e.g., semantic HTML, ARIA labels where necessary).

### 2. Testing
- [ ] **Unit Tests:** All new functionality has corresponding unit tests, and existing tests pass.
- [ ] **Integration Tests:** Critical integration points have been tested.
- [ ] **No Major Bugs:** No high-priority or critical bugs are known to exist.
- [ ] **Manual Testing:** The feature has been manually tested by the developer in a staging environment.

### 3. Documentation & User Experience
- [ ] **Code Comments:** Any complex logic or public API has appropriate code comments.
- [ ] **User-Facing Documentation:** Any changes to user-facing features have been communicated for the user manual or help section.
- [ ] **Changelog:** A summary of the change is added to the `CHANGELOG.md` file under the correct version and change type.
- [ ] **Versioning:** If a public API has changed, the version has been updated according to Semantic Versioning.

### 4. Deployment & Integration
- [ ] **Build Passes:** The code builds successfully in the CI/CD pipeline without errors.
- [ ] **All Tests Pass:** All automated tests (unit, integration, end-to-end) pass in the CI/CD pipeline.
- [ ] **Successfully Deployed:** The Increment has been successfully deployed to a staging environment or is ready for production deployment.
- [ ] **Definition of Done (DoD) Met:** The item fulfills the Sprint Goal and is integrated with previous Increments without breaking existing functionality.

---

## Exceptions and Special Cases

- **Bugs:** A bug fix is "done" when it **meets all the criteria above**, especially the testing criteria. A bug fix is not complete until a test confirms the issue is resolved.
- **Hotfixes:** May bypass some peer-review and full documentation steps, but they still require a successful build and a test confirming the fix. A separate task must be created to add tests and update the changelog post-deployment.

## Last Word
If a Product Backlog item does not meet the Definition of Done, it is **not an Increment**. It cannot be released or presented at the Sprint Review and must be returned to the Product Backlog.