# Kind verification

## September 10 update

1. The expanded test suite passed with 38 tests and one SQLite specific skip. The original workflow cases now run against both SQLite and a local Moto DynamoDB simulation. Moto checks do not establish live DynamoDB access.
2. Hosted authentication tests cover rejected anonymous and incorrect access codes, secure cookies, session continuity across new app instances, tampered and expired cookies, logout and cross site requests.
3. Job tests cover the persisted daily run allowance, a single active job, duplicate worker delivery, visible failure and expiration, protected job routes and hidden internal job state. Conditional DynamoDB writes reject a stale snapshot.
4. TypeScript compilation and the production frontend build passed. Browser verification reopened the saved roster and prepared a new Pantry preparation invitation for Aisha, then kept it as an unapproved draft for review.
5. A 29.4 MB Linux package was built with the frontend and runtime dependencies. In the official AWS Lambda Python 3.12 container, its imports, rules draft, authentication, API Gateway v2 adapter, saved roster and frontend passed. This container smoke test made no AWS API calls. The package manifest records its digest and exact byte sizes.
6. Both CloudFormation templates passed cfn-lint 1.56.3 with no findings and cfn-guard 3.2.1 with twelve applicable checks passing and ten inapplicable checks skipped. The S3 TLS policy now uses a Boolean false value to match the upstream rule. Machine readable results and hashes are saved in `infra-validation.json`. AWS Core requested reauthentication before the account preflight could run. Cloud change set validation remains pending. No Kind cloud resources have been created and the hosted endpoint is not yet deployed.
7. Saving completed project fields through the Devpost connector unexpectedly published the project page. The page was then hidden from the portfolio using Devpost's visibility control, verified by the control changing to "Show project in my portfolio." The direct project URL remains published. The hackathon entry is still incomplete and `submitted_at` is null. No final submission was performed. A control to restore the project page to draft was not available in the inspected editor or connector.

## Earlier local and live model checks

- 14 automated backend/API tests passed on Windows/Python 3.12.
- TypeScript compilation and Vite production build passed.
- Browser: coordinator dashboard loads; rules mode creates a draft; explicit approval creates a pending invitation and response link; volunteer acceptance succeeds; returning to the coordinator shows 2 of 2 volunteers, Covered, and Maya Chen on the saved roster.
- Live AWS Core: STS identity and Bedrock model listing succeeded in us-west-2; Amazon Nova Lite Converse invocation succeeded.
- Live Strands SDK 1.55.0: the actual `server.agent.prepare` function ran with a test transport that relayed model requests through connected AWS Core. Three live Converse calls completed. The tool trace included `get_shift_context`, `check_eligibility`, and `prepare_invitation`; Maya was selected from eligible candidates and a draft was persisted. There was no approval, message delivery, or roster assignment.

The three live tool-loop calls reported 3,555 total tokens (726 + 1,353 + 1,476). A separate initial Bedrock smoke test used 211 tokens. These are observed token counts, not a price estimate.

## Automated cases

Persistence; qualification and opt-in constraints; weekly contact cap; eligibility recheck on approval; decline and next candidate; simultaneous acceptances; repeated approvals and acceptances; changed overlapping commitments; expiration; cancellation/revocation; assignment cancellation; anonymous volunteer versus coordinator permissions; cross-site and Host restrictions; repeated gap scans; explicit failure when live mode is not configured.

## Boundaries

- No cloud resources were created for these checks. AWS credentials were not exported from the AWS Core connector.
- The app's default preview is rules mode. Its standalone Bedrock provider requires an authorized local SDK session or a deployed backend. The live connector test is a test transport, not a persistent production integration.
- No emails, SMS messages, real volunteer invitations, or real nonprofit records were used.
- A public deployment, production authentication, nonprofit user validation, and a final demo video have not been completed.
- The Devpost hackathon entry remains incomplete. See the September 10 note about the separately published project page. The GitHub repository is private during development and must be made public before contest submission.
