# Kind — submission working copy

The complete current packet is [devpost-submission.md](../devpost-submission.md), including confirmed individual entry, official field IDs, judging instructions and captured asset locations. This shorter writeup remains useful for the project description.

Track: Good Neighbor Agents

Tagline: Keep volunteer shifts covered, so coordinators can focus on their community.

## Inspiration

A volunteer cancellation creates work well beyond one empty cell on a schedule: someone has to check availability, confirm qualifications, ask for help, process replies, and keep the roster accurate. Kind focuses on that complete coordination loop.

## What it does

Kind identifies uncovered shifts in a sample nonprofit roster, finds eligible volunteers, and prepares invitations for a coordinator to review. After approval, a volunteer can accept or decline through an individual response page. Acceptance updates the roster atomically, while declines keep the gap visible for the coordinator.

## How we built it

The interface uses React, TypeScript, and Vite. A Python/FastAPI backend stores the local workflow in SQLite. The deployed AWS version uses DynamoDB, coordinator access control, API Gateway and a private Lambda worker for AI preparation, with a persisted daily usage limit. A Strands agent uses Amazon Bedrock to read shift context, check eligibility and stage an invitation. Approval and assignment are separate server controlled steps beyond the model's tool permissions. An explicit rules mode supports demonstrations without model calls.

## What we verified

The expanded suite passed 48 tests, with one database specific skip, covering the workflow on SQLite and simulated DynamoDB, coordinator access, competing responses, sample restart, time conversion and background job boundaries. The local browser workflow was exercised through acceptance and roster readback. The packaged application passed a smoke test inside the official Lambda Python container. The deployed HTTPS API and browser then completed real Strands and Nova Lite preparation, approval and volunteer acceptance workflows. Repeated acceptance did not overfill the shift, and the roster remained saved after sign out and a new session.

## Challenges and what we learned

Running the complete flow exposed problems a recommendation mockup would miss. Hosted AI preparation needed an asynchronous worker so the browser could poll while the model ran. A shared sample also needed a confirmed restart so judges could try future shifts without renewing the paid AI allowance. Finally, a recorded live model run converted a shift time incorrectly. The invitation tool now formats dates, times and location directly from the saved shift; the model selects the volunteer and stages the draft while the coordinator retains editing and approval.

## What remains before submission

- Judge access instructions for the deployed build at https://idwgz9gl09.execute-api.us-west-2.amazonaws.com. The private coordinator code must be shared through an appropriate judging access field, not a public project description.
- Public repository visibility and final source/license review.
- A public video of at most five minutes, showing the real working flow.
- Final architecture and testing instructions checked against the shipped build.
- AWS Builder ID and other user-only submission fields.
- Explicit final submission approval.

All people and organizations in the current demo are fictional. Deployment is verified. No claims of adoption, volunteer hours saved, or external message delivery should be added without evidence.
