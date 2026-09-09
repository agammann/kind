# Kind

**Keep volunteer shifts covered, so coordinators can focus on their community.**

Kind is a working local prototype for the **Good Neighbor Agents** track of the Agents for Humans Hackathon. It combines an accountable volunteer-coverage workflow with a Strands Agents integration for Amazon Bedrock.

## What works

- A responsive coordinator dashboard, volunteer directory, and saved activity history.
- A SQLite-backed roster with fictional volunteers and shifts, clearly labeled in the interface.
- Background gap detection every 30 seconds while the backend is running.
- Eligibility checks for full-shift availability, qualifications, existing assignments, opt-in, and a three-invitation weekly contact limit.
- Deterministic rules mode that prepares a draft without making model calls.
- A real Strands agent with three bounded tools: `get_shift_context`, `check_eligibility`, and `prepare_invitation`.
- Human review and editing before an invitation becomes an active response link.
- A volunteer page with accept/decline actions. Acceptance atomically updates the roster, with current eligibility and remaining capacity rechecked.
- Idempotent repeat approvals/responses, expired and revoked links, and competing acceptances handled without overfilling.

**Approval does not send email or SMS.** It creates an in-app response link. The local link works only where this local server is accessible. No messaging service is configured, and the prototype is not deployed.

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

## Live Strands + Bedrock

The normal app uses the AWS SDK credential chain. Use an existing authorized local AWS session and a model that your account can invoke. Never paste credentials into the source or browser.

```powershell
$env:AWS_REGION = 'us-west-2'
$env:KIND_BEDROCK_MODEL_ID = 'amazon.nova-lite-v1:0'
python -m uvicorn server.app:app --host 127.0.0.1 --port 8000 --no-access-log
```

Select **Strands + Amazon Bedrock** in the preparation panel. Each run has a five-model-call ceiling and an explicit 900-token output limit per call. Live calls incur Bedrock usage charges. The agent can inspect candidates and stage an invitation, but cannot approve, send, or assign a volunteer. The UI reports provider failures instead of silently substituting rules mode.

**Verification boundary:** the real local Strands tool loop was exercised with live Bedrock responses relayed through the connected AWS Core tool in Codex. That test did not export AWS credentials or create cloud resources. It proves the tool loop with a live model; it does not provide a persistent AWS connection to the standalone app. The default runnable preview uses rules mode until local AWS credentials or a deployed backend are configured. See [verification](docs/verification.md).

## Tests

```sh
python -m pytest -q
pnpm build
```

The tests cover persistent state, approval boundaries, eligibility changes, contact limits, declines, concurrent acceptance, repeat requests, assignment conflicts, expiration, revocation, gap detection, API authorization, and cross-site request rejection.

## Architecture and limits

See [architecture](docs/architecture.md), [scope](docs/scope.md), [verification](docs/verification.md), and [submission draft](docs/submission-draft.md).

This is a **single-organization, local sample workspace**, not a production multi-tenant service. Coordinator sessions are bootstrapped locally, volunteer links are bearer links, and SQLite serializes writes. Bind only to loopback. Do not expose this server publicly without replacing local session bootstrap with proper coordinator authentication, configuring HTTPS and trusted origins, and selecting durable hosted storage. No real nonprofit adoption or impact metrics are claimed.

## Built with

Strands Agents SDK · Amazon Bedrock · Python · FastAPI · SQLite · React · TypeScript · Vite · Lucide

## License and attribution

MIT; see [LICENSE](LICENSE). Built with assistance from OpenAI Codex. The initial visual concept was generated with the built-in image-generation tool; the functional interface is implemented in React/CSS. Lucide icons are distributed under the ISC license; DM Sans and Manrope use the SIL Open Font License. No pre-existing project implementation was reused. All volunteer and organization records are fictional.

