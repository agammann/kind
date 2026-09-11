## Inspiration

A volunteer cancellation creates work well beyond one empty cell on a schedule: someone has to check availability, confirm qualifications, ask for help, process replies, and keep the roster accurate. Kind focuses on that complete coordination loop in the **Good Neighbor Agents** track.

## What it does

Kind identifies uncovered shifts in a sample nonprofit roster, finds eligible volunteers, and prepares invitations for a coordinator to review. After approval, a volunteer can accept or decline through an individual response page. Acceptance updates the roster atomically, while declines keep the gap visible for the coordinator.

The coordinator stays in control. The agent can read context, check eligibility and stage a draft, but it cannot approve an invitation or assign a volunteer. Approval creates a response link; it does not send email or SMS.

## How we built it

The interface uses React, TypeScript and Vite. A Python and FastAPI backend stores the local workflow in SQLite. The deployed AWS version uses DynamoDB, coordinator access control, API Gateway and a private Lambda worker for AI preparation, with a persisted daily usage limit.

A Strands agent uses Amazon Bedrock and Amazon Nova Lite to read shift context, check eligibility and stage an invitation. Approval and assignment are separate server controlled steps beyond the model's tool permissions. An explicit rules mode supports demonstrations without model calls.

## Challenges and what we learned

Hosted AI preparation needed an asynchronous worker so the browser could poll while the model ran. A shared sample also needed a confirmed restart so judges could try future shifts without renewing the paid AI allowance.

A recorded live model run converted a shift time incorrectly. The invitation tool now formats dates, times and location directly from the saved shift. The model selects the volunteer and stages the draft while the coordinator retains editing and approval.

## What we verified

The expanded suite passed **48 tests, with one database specific skip**, covering the workflow on SQLite and simulated DynamoDB, coordinator access, competing responses, sample restart, time conversion and background job boundaries.

The local browser workflow was exercised through acceptance and roster readback. The packaged application passed a smoke test inside the official Lambda Python container. The deployed HTTPS API and browser then completed real Strands and Nova Lite preparation, approval and volunteer acceptance workflows. Repeated acceptance did not overfill the shift, and the roster remained saved after sign out and a new session.

## Try Kind

The [hosted AWS demo](https://idwgz9gl09.execute-api.us-west-2.amazonaws.com) uses a coordinator access code and a shared fictional sample. The [source repository](https://github.com/agammann/kind) includes the MIT license, setup instructions, architecture diagram and verification notes.

All people and organizations in the demo are fictional. Kind is a working hackathon prototype. No real nonprofit adoption, measured volunteer hours saved or external message delivery is claimed.

