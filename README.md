# Kind

**Keep volunteer shifts covered, so coordinators can focus on their community.**

**Narrated demo:** [Watch Kind on YouTube](https://www.youtube.com/watch?v=XjpDlKANTAY). This three minute recording shows the actual deployed workflow with Amazon Polly Matthew narration and captions.

Kind is a working volunteer coordinator for the **Good Neighbor Agents** track of the Agents for Humans Hackathon. It combines a volunteer coverage workflow with Strands Agents and Amazon Bedrock, and runs locally or as a protected AWS sample demo.

**Hosted demo:** [Open Kind](https://idwgz9gl09.execute-api.us-west-2.amazonaws.com). Coordinator access requires the private demo code. All organization and volunteer records are fictional. The live preparation, approval, acceptance and saved roster workflow has been verified; see [live verification](docs/live-verification.json).

## What works

- A responsive coordinator dashboard, volunteer directory, and saved activity history.
- A saved roster with fictional volunteers and shifts, using SQLite locally and DynamoDB on AWS.
- Coverage checks every 30 seconds in the local server, and when the coordinator workspace loads or polls on AWS.
- Eligibility checks for full-shift availability, qualifications, existing assignments, opt-in, and a three-invitation weekly contact limit.
- Deterministic rules mode that prepares a draft without making model calls.
- A real Strands agent with three bounded tools: `get_shift_context`, `check_eligibility`, and `prepare_invitation`.
- Invitation wording formatted from saved shift facts, with local time and daylight saving conversion handled by the server. The model selects an eligible volunteer and stages the draft; the coordinator can edit its text.
- Human review and editing before an invitation becomes an active response link.
- A volunteer page with accept/decline actions. Acceptance atomically updates the roster, with current eligibility and remaining capacity rechecked.
- Idempotent repeat approvals/responses, expired and revoked links, and competing acceptances handled without overfilling.

**Approval does not send email or SMS.** It creates an in-app response link. Hosted links work over HTTPS; local links work only where the local server is accessible. No messaging service is configured.

## Run locally

Prerequisites: Python 3.12+ and Node.js 22+ with pnpm. The development run used Python 3.12, Node 24, pnpm 11, and Strands 1.55.0.

```sh
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```sh
# macOS / Linux
source .venv/bin/activate
```

Install the app, build the interface, and start it:

```sh
pip install -r requirements.txt
pnpm install
pnpm build
python -m uvicorn server.app:app --host 127.0.0.1 --port 8000 --no-access-log
```

Open **http://127.0.0.1:8000**. The server creates `data/kind.sqlite3` on its first run. That file is private local state and is excluded from Git. `requirements-lock.txt` records the exact Windows verification environment; `requirements.txt` is portable across platforms.

For frontend development, keep the Python server running and use `pnpm dev` in another terminal. Vite serves the interface at http://127.0.0.1:5173 and proxies `/api` to port 8000.

## Try the complete workflow

1. Select **Saturday food distribution**.
2. Keep **Rules mode · no AI calls** selected, then click **Prepare invitation**.
3. Review/edit the invitation and click **Approve invitation**.
4. Open **Response page**, then choose **I can help**.
5. Return to the coordinator workspace. The shift is covered and Maya is on the roster.
6. Use another open shift to try **Not this time**, then prepare an invitation for the next eligible person.
7. Use **Record cancellation** to reopen a covered shift. Kind will avoid immediately re-inviting the person who cancelled.

The hosted sample may already be covered from verification or another review. Use **Restart sample** in the footer and review the confirmation to create fresh future shifts. This replaces the shared fictional roster and invalidates previous sample links, while preserving the daily AI allowance. It refuses to run during an active preparation. To exercise the model, choose **Strands + Amazon Bedrock** before preparing an invitation.

## Live Strands + Bedrock

The normal app uses the AWS SDK credential chain. Use an existing authorized local AWS session and a model that your account can invoke. Never paste credentials into the source or browser.

```powershell
$env:AWS_REGION = 'us-west-2'
$env:KIND_BEDROCK_MODEL_ID = 'amazon.nova-lite-v1:0'
python -m uvicorn server.app:app --host 127.0.0.1 --port 8000 --no-access-log
```

Select **Strands + Amazon Bedrock** in the preparation panel. Each run has a five-model-call ceiling and an explicit 900-token output limit per call. Live calls incur Bedrock usage charges. The agent can inspect candidates and stage an invitation, but cannot approve, send, or assign a volunteer. The UI reports provider failures instead of silently substituting rules mode.

**Verification boundary:** an initial local tool loop was tested through AWS Core without exporting credentials. The deployed Lambda worker now uses its own scoped IAM role and has completed the actual live workflow through the HTTPS API, independently of Codex. The local preview still defaults to rules mode unless an authorized SDK session is configured. See [verification](docs/verification.md).

## Tests

```sh
python -m pytest -q
pnpm build
```

The tests cover persistent state, approval boundaries, eligibility changes, contact limits, declines, concurrent acceptance, repeat requests, assignment conflicts, expiration, revocation, gap detection, API authorization, and cross-site request rejection.

## Architecture and limits

See [architecture](docs/architecture.md), [scope](docs/scope.md), [verification](docs/verification.md), [AWS deployment plan](docs/aws-deployment.md), and the [complete submission draft](devpost-submission.md).

This is a **single organization sample workspace**, not a service for real nonprofit operations. Local mode bootstraps coordinator sessions and binds only to loopback. Hosted mode requires an access code and uses secure signed cookies, a trusted HTTPS origin and DynamoDB. Volunteer links are bearer links. Managed identity, organization isolation, operational data entry, backup procedures and user validation remain future work. No real nonprofit adoption or impact metrics are claimed.

## Deployed AWS demo

The CloudFormation templates are deployed in `us-west-2`. Hosted mode requires a coordinator access code, uses signed secure session cookies, persists the sample roster in DynamoDB, and queues live AI work in a separate Lambda worker. Conditional writes prevent competing requests from overwriting a newer roster. A persisted counter admits at most 20 live AI runs per UTC day by default. AWS hosting and Bedrock usage are metered; the run limit is not a dollar cap.

The hosted demo is one shared fictional organization. It is not an identity service for real nonprofit operations. The deployment plan describes resources, costs and access boundaries; [deployment evidence](docs/deployment.json) records the verified runtime state and package digest.

For the full test suite, install `pip install -r requirements-test.txt` before running `python -m pytest -q`. DynamoDB tests run against Moto locally and do not access AWS.

## Built with

Strands Agents SDK · Amazon Bedrock · AWS Lambda · Amazon DynamoDB · API Gateway · Python · FastAPI · SQLite · React · TypeScript · Vite · Lucide

## License and attribution

MIT; see [LICENSE](LICENSE). Built with assistance from OpenAI Codex. The initial visual concept was generated with the built-in image-generation tool; the functional interface is implemented in React/CSS. Lucide icons are distributed under the ISC license; DM Sans and Manrope use the SIL Open Font License. No pre-existing project implementation was reused. All volunteer and organization records are fictional.

Selected AWS Guard validation rules are included under their separate Apache 2.0 license in `infra/guard/LICENSE`; their pinned upstream source is documented in `infra/guard/README.md`.
