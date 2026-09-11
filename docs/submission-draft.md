# Kind — submission working copy

Track: Good Neighbor Agents

Tagline: Keep volunteer shifts covered, so coordinators can focus on their community.

## Inspiration

A volunteer cancellation creates work well beyond one empty cell on a schedule: someone has to check availability, confirm qualifications, ask for help, process replies, and keep the roster accurate. Kind focuses on that complete coordination loop.

## What it does

Kind identifies uncovered shifts in a sample nonprofit roster, finds eligible volunteers, and prepares invitations for a coordinator to review. After approval, a volunteer can accept or decline through an individual response page. Acceptance updates the roster atomically, while declines keep the gap visible for the coordinator.

## How we built it

The interface uses React, TypeScript, and Vite. A Python/FastAPI backend stores the local workflow in SQLite. The deployed AWS version uses DynamoDB, coordinator access control, API Gateway and a private Lambda worker for AI preparation, with a persisted daily usage limit. A Strands agent uses Amazon Bedrock to read shift context, check eligibility and stage an invitation. Approval and assignment are separate server controlled steps beyond the model's tool permissions. An explicit rules mode supports demonstrations without model calls.

## What we verified

The expanded suite passed 38 tests, with one database specific skip, covering the workflow on SQLite and simulated DynamoDB, coordinator access, competing responses and background job boundaries. The local browser workflow was exercised through acceptance and roster readback. The packaged application passed a smoke test inside the official Lambda Python container. The deployed HTTPS API then completed the real Strands and Nova Lite preparation, approval and volunteer acceptance workflow. Repeated acceptance did not overfill the shift, and the roster remained saved after sign out and a new session.

## What remains before submission

- Judge access instructions for the deployed build at https://idwgz9gl09.execute-api.us-west-2.amazonaws.com. The private coordinator code must be shared through an appropriate judging access field, not a public project description.
- Public repository visibility and final source/license review.
- A public video of at most five minutes, showing the real working flow.
- Final architecture and testing instructions checked against the shipped build.
- AWS Builder ID and other user-only submission fields.
- Explicit final submission approval.

All people and organizations in the current demo are fictional. No claims of deployment, adoption, volunteer hours saved, or external message delivery should be added without evidence.
