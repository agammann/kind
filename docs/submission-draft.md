# Kind — submission working copy

Track: Good Neighbor Agents

Tagline: Keep volunteer shifts covered, so coordinators can focus on their community.

## Inspiration

A volunteer cancellation creates work well beyond one empty cell on a schedule: someone has to check availability, confirm qualifications, ask for help, process replies, and keep the roster accurate. Kind focuses on that complete coordination loop.

## What it does

Kind identifies uncovered shifts in a sample nonprofit roster, finds eligible volunteers, and prepares invitations for a coordinator to review. After approval, a volunteer can accept or decline through an individual response page. Acceptance updates the roster atomically, while declines keep the gap visible for the coordinator.

## How we built it

The interface uses React, TypeScript, and Vite. A Python/FastAPI backend stores the workflow in SQLite. A Strands agent can read shift context, check eligibility, and stage an invitation with Amazon Bedrock. Approval and assignment are separate server-controlled steps, beyond the agent's tool permissions. An explicit rules mode supports offline demonstrations.

## What we verified

Fourteen automated tests cover persistence, eligibility, approval boundaries, and conflicting volunteer responses. The local browser workflow was exercised through acceptance and roster read-back. The real Strands tool loop was also tested with live Bedrock responses through AWS Core; standalone app credentials/hosting remain to be configured.

## What remains before submission

- A judge-accessible working build with the intended live model integration.
- Public repository visibility and final source/license review.
- A public video of at most five minutes, showing the real working flow.
- Final architecture and testing instructions checked against the shipped build.
- AWS Builder ID and other user-only submission fields.
- Explicit final submission approval.

All people and organizations in the current demo are fictional. No claims of deployment, adoption, volunteer hours saved, or external message delivery should be added without evidence.
