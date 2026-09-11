# Kind — submission working copy

Track: Good Neighbor Agents

Tagline: Keep volunteer shifts covered, so coordinators can focus on their community.

## Inspiration

A volunteer cancellation creates work well beyond one empty cell on a schedule: someone has to check availability, confirm qualifications, ask for help, process replies, and keep the roster accurate. Kind focuses on that complete coordination loop.

## What it does

Kind identifies uncovered shifts in a sample nonprofit roster, finds eligible volunteers, and prepares invitations for a coordinator to review. After approval, a volunteer can accept or decline through an individual response page. Acceptance updates the roster atomically, while declines keep the gap visible for the coordinator.

## How we built it

The interface uses React, TypeScript, and Vite. A Python/FastAPI backend stores the local workflow in SQLite. A Strands agent can read shift context, check eligibility, and stage an invitation with Amazon Bedrock. Approval and assignment are separate server controlled steps, beyond the agent's tool permissions. An explicit rules mode supports offline demonstrations. The prepared AWS version uses DynamoDB persistence, coordinator access control, and a private Lambda worker for AI preparation, with a persisted daily usage limit. That version has not yet been deployed.

## What we verified

The expanded suite passed 38 tests, with one database specific skip, covering the workflow on SQLite and simulated DynamoDB, coordinator access, competing responses and background job boundaries. The local browser workflow was exercised through acceptance and roster readback. The packaged application passed a smoke test inside the official Lambda Python container. The real Strands tool loop was also tested with live Bedrock responses through AWS Core; the standalone live endpoint remains to be deployed and verified.

## What remains before submission

- A judge-accessible working build with the intended live model integration.
- Public repository visibility and final source/license review.
- A public video of at most five minutes, showing the real working flow.
- Final architecture and testing instructions checked against the shipped build.
- AWS Builder ID and other user-only submission fields.
- Explicit final submission approval.

All people and organizations in the current demo are fictional. No claims of deployment, adoption, volunteer hours saved, or external message delivery should be added without evidence.
