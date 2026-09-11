# Verification — 2026-09-09 UTC

## Completed

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
- The Devpost project is a draft. The GitHub repository is private during development and must be made public before contest submission.
