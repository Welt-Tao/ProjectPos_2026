# Project plan

Owner: Taoliyuan. Individual project, permitted by the course tutor.
Deadline: 24 November 2026. Working language: English.

## Scope and assumptions

Cash sales and receipt-based cash returns in one small supermarket. Python standard library, SQLite persistence, and an English browser interface served only on localhost. Currency is EUR, with tax-inclusive prices. Returns require the original receipt, cannot exceed unreturned quantities, and restore saleable goods to stock. No card integration, login, discount engine, damaged-goods workflow or deployment to the public internet.

## Planned sprints

This is a Scrum-inspired individual adaptation. One person owns product priorities, development and reviews. No group ceremonies or stakeholder feedback are claimed without evidence. Each sprint is a three-day timebox, which may deliver its increment early. Actual work dates and checkpoints are recorded separately from this plan.

1. Sprint 1, 15–17 October 2026: cash sale, stock persistence and receipt. Acceptance: two milk units and one bread cost EUR 8.20; EUR 10 produces EUR 1.80 change; stock falls by the purchased quantities.
2. Sprint 2, 18–20 October 2026: returns and transaction history. Acceptance: one milk unit refunds EUR 2.50 at the original price and restores one unit; excess returns fail without writes.
3. Sprint 3, 21–23 October 2026: UML, report, presentation, repository publication and user rehearsal. Acceptance: traceable diagrams, passing checks, readable deliverables, working remote branches and a recorded demonstration.

Early implementation of later-sprint features is recorded as early delivery, without inventing elapsed days. Video recording, public upload and student acceptance remain open until performed.

## Definition of done

Acceptance criteria checked; meaningful automated tests pass; interface exercised; documentation and UML match code; changes committed on the individual branch then merged to main; branches preserved. Submission is complete only after the GitHub repository and Bilibili video URLs are verified and included in the report.

## Risks

Publication access may require the owner to sign in. Recording requires the student's narration and review. SQLite is appropriate for a local demonstration but not a distributed retail deployment. Back up the data folder before changing or removing it.
