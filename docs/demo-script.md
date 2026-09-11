# Kind demo narration and recording plan

The prepared video is a screen recording of the deployed HTTPS app, with editorial title cards and captions. It has no narration audio. Its runtime is under five minutes. The captions carry the pitch; this text can also be read as an optional voiceover.

## Opening

When a volunteer cancels, a nonprofit coordinator has to find eligible help, ask, track the reply and update the roster. Kind handles that loop with a human approval step. It is built for the Good Neighbor Agents track, helping small nonprofits and food banks keep volunteer shifts covered.

## Working flow

This is the deployed AWS app. All people and organizations shown are fictional. Pantry preparation needs one volunteer. Kind checks full shift availability, required qualifications, overlapping assignments, opt in and recent invitation load.

We select Strands plus Amazon Bedrock. A private Lambda worker runs the real Nova Lite model. The agent can read shift context, check eligibility and prepare a draft. It has no tool to approve an invitation or assign a person.

The draft is ready for review. The coordinator can edit the exact message before approving it. Approval creates a scoped volunteer response link. This sample does not send email or SMS; the link is shared manually.

The volunteer sees their invitation and shift, then chooses whether to help. Acceptance rechecks eligibility and remaining capacity, then saves the assignment. Repeat responses cannot overfill the shift.

Back in the coordinator view, the shift is covered and the saved activity explains what happened. The preparation history shows the real Strands tool activity. Model preparation remains separate from human approval and volunteer acceptance.

Judges can restart the fictional sample to create future shifts and try the flow again. The confirmation explains that this replaces shared demo data and invalidates old links. It preserves the daily AI allowance and refuses to run during an active preparation.

## Closing

React and FastAPI serve the coordinator and volunteer workflow. A private Lambda worker runs Strands and Bedrock. DynamoDB uses conditional writes to protect the roster. The intended benefit is less coordination work and more reliable coverage, with a clear human decision before contacting a volunteer.

Kind is a working fictional sample ready for feedback from nonprofit coordinators. No real nonprofit adoption or measured time savings are claimed. Codex assisted with the design, implementation, tests, deployment and verification.

## Publication checklist

1. Review the final local video, including its title cards, live AI labels and readable captions.
2. Upload the video to a supported public video host. Do not publish the coordinator access code or raw volunteer bearer URLs.
3. Add the resulting public video URL to the Devpost project only after publication approval.
4. Attach the architecture PNG and select a few working UI screenshots.
5. Verify judge access, public repository visibility, personal declarations and final submission separately.
