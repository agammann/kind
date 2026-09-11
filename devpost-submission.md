# Kind

## One-line Summary

Keep volunteer shifts covered, so coordinators can focus on their community.

## Problem

When a volunteer cancels, a small nonprofit's coordinator has to check who is available, confirm qualifications, ask for help, track the answer and update the roster. A replacement recommendation alone leaves most of that work unfinished.

## Solution

Kind turns a coverage gap into a reviewed invitation and a saved volunteer response. It identifies an uncovered shift, checks eligible volunteers, and uses a Strands agent to prepare an invitation. The coordinator reviews the exact text before approving a response link. The volunteer can accept or decline; acceptance rechecks eligibility and capacity before updating the roster.

## Why This Matters

Kind is for small nonprofits and food banks coordinating a shared volunteer schedule. The intended benefit is less time spent chasing replies and fewer unfilled shifts. Its Good Neighbor Agents focus is helping a group deliver community services while respecting each volunteer's availability, consent and recent contact load. These are intended benefits, not measured outcomes: the current organization and people are fictional, and no real nonprofit adoption is claimed.

## How We Used AI

Strands Agents SDK runs in a private AWS Lambda worker and uses Amazon Bedrock Nova Lite. Its tools are `get_shift_context`, `check_eligibility` and `prepare_invitation`. The model reads bounded context, checks candidates and stages one invitation. The tool formats invitation wording from the saved shift, including the correct local time, date and location. The coordinator can then edit it. Eligibility rules, coordinator approval and atomic assignment run outside the model's authority. The agent has no approval, messaging or assignment tool.

Each run allows at most five model calls and 900 output tokens per call. A persisted allowance admits at most 20 live AI runs per UTC day. A separate, explicitly labeled rules mode is available without model calls. Provider errors are shown instead of silently replacing AI with rules.

## How We Used Codex

Codex assisted with the React interface, Python workflow, tests, AWS templates and deployment. It helped separate model preparation from human approval, verify eligibility and concurrent response boundaries, and exercise the real deployed workflow. The initial visual concept was generated with the image generation tool; the functional interface is React and CSS. Codex also identified that fixed sample dates would expire before judging and added a confirmed sample restart that preserves the AI allowance.

## Key Features

1. Coverage view, volunteer directory and persistent activity history.
2. Full shift availability, qualification, overlap, opt in and contact limit checks.
3. Real Strands preparation, with a separately labeled rules mode.
4. Editable invitation review before a response link becomes active.
5. Scoped volunteer acceptance and decline pages.
6. Atomic roster updates and protection against duplicate or competing responses.
7. Protected hosted coordinator access and bounded asynchronous AI work.
8. Confirmed restart of fictional data with fresh future shifts for repeatable judging.

## Architecture

React and TypeScript provide the interface. API Gateway routes HTTPS requests to FastAPI on Lambda. Coordinator sessions use a random access code and signed secure cookies. DynamoDB stores the shared fictional roster using conditional versioned writes. The API admits a bounded job and invokes the private Strands worker; the browser polls for its result. S3 stores the private deployment package. CloudWatch records logs, and an encrypted SQS queue receives failed worker deliveries.

The same workflow runs locally with SQLite. AWS Lambda is the deployed runtime; AgentCore is not used.

Architecture attachment: `docs/assets/kind-architecture.png` (1800 × 1260). Editable SVG is alongside it. The rendered PNG has been reviewed and is ready to attach to official field 27734.

## Testing Instructions

Open the hosted demo and sign in with the separately provided coordinator access code. This is one shared fictional workspace. If the sample shifts are already filled or have passed, use **Restart sample** in the footer and review the confirmation before replacing the shared sample data. Restarting invalidates previous sample links but does not renew the daily AI allowance.

1. Choose **Saturday food distribution** in a fresh sample. It needs one more volunteer.
2. Select **Strands + Amazon Bedrock**, then **Prepare invitation**. Allow the background job to finish.
3. Review the draft. The roster remains unchanged and there is no active response link yet.
4. Edit the invitation if desired and choose **Approve invitation**. This creates a response link; no email or SMS is sent.
5. Open **Response page** and choose **I can help**. The volunteer sees confirmation.
6. Return to the coordinator workspace and check the covered shift and activity history.
7. Open **Activity** and expand the Strands preparation entry to inspect tool activity.
8. Optionally use **Pantry preparation** to try **Not this time** and observe the saved decline.

If the live daily allowance has been used, **Rules mode · no AI calls** can exercise the workflow. This is not a live AI demonstration. For independent local testing, follow README.md; a fresh local database creates future sample dates. Use an authorized AWS SDK session for local model calls.

Access code handling: the local file `deployment-private/coordinator-access.txt` is private and ignored by Git. Do not paste it into the public project description, video or screenshots. Confirm how the host accepts restricted judge access instructions before providing it through a form.

## Public Demo Link

https://idwgz9gl09.execute-api.us-west-2.amazonaws.com

HTTPS endpoint is deployed. Coordinator access requires the demo code. Volunteer links are scoped bearer links.

## Public Repository Link

https://github.com/agammann/kind

The repository currently remains private. Public visibility is an official requirement and still requires the owner's release approval. The repository includes an MIT LICENSE; verify GitHub detects it after release.

## Demo Video

Public URL: TODO after reviewing and uploading the prepared video.

Target: a captioned screen demonstration under five minutes, covering the problem, audience, working flow and why it matters. The recording uses the actual deployed app, editorial title cards and captions. No real people, external messages or impact metrics are represented. The selected version uses Matthew neural narration from Amazon Polly, with the existing captions retained.

Local video: `../kind-submission/kind-demo-narrated.mp4`. The recording evidence file contains timing and actual browser checks. [Demo narration and publication instructions](docs/demo-script.md) accompany it. Do not call a local video a public URL.

## Screenshot Shot List

1. Coverage gap and candidate eligibility.
2. Real model invitation waiting for coordinator review.
3. Scoped volunteer response page.
4. Covered roster after acceptance.
5. Saved agent tool history.

Assets are in `../kind-submission/`. Use the matching captured PNG files, not conceptual design images.

## Submission Readiness Notes

Official requirements and judging criteria were fetched live through the Devpost connector on September 10, 2026 Pacific. The deadline is September 14, 2026 at 5:00 p.m. Pacific (September 15 at 00:00 UTC). The host requires a public code repo, MIT or Apache license, README, architecture attachment, maximum five minute demo video, and AWS Builder ID. A live demo and optional Builder blog post can strengthen the entry. AgentCore is optional.

The updated local test suite passed 48 tests, with one database specific skip. The frontend built successfully, and the updated package passed the official Lambda Python 3.12 container smoke test. The original deployed live API workflow passed nine checks. The recording pass separately verifies the updated deployed interface.

The existing Devpost project page is published; the hackathon entry has no submitted timestamp. This packet is a local draft and has not been applied to the public project page. Required user declarations and final confirmation remain outstanding.

## Known Limitations

One shared fictional organization; no managed user identities, organization isolation, real operational data entry, nonprofit user validation or measured impact. No email/SMS delivery. Restarting the sample changes the shared demo for other reviewers and invalidates old links, so it requires explicit confirmation. AWS usage is metered; the daily AI admission count is not a hard dollar cap. No continuous AWS background watcher is claimed: hosted coverage checks occur when the coordinator loads or polls the workspace.

## TODO Official Form Fields

| Field | ID | Draft value or required action |
| --- | --- | --- |
| Submitter Type | 27729 | Individual, confirmed by the user |
| Country of Residence | 27730 | TODO user confirmation |
| Organization name | 27731 | Not applicable for an individual entry |
| Track | 27732 | Good Neighbor Agents |
| PUBLIC code repo | 27733 | https://github.com/agammann/kind ; public visibility pending |
| Architecture diagram | 27734 | Attach kind-architecture.png; do not put a text answer in this file field |
| AWS Builder ID | 27735 | TODO user supplied Builder ID |
| Live demo | 27736 | https://idwgz9gl09.execute-api.us-west-2.amazonaws.com |
| Testing instructions | 28191 | Use Testing Instructions above; settle private code delivery first |
| Optional bonus blog | 27737 | Omit unless an actual post is publicly published on builder.aws |

The fetched official form does not ask for a Codex session ID. Do not add one.
