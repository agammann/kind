# Kind narrated demo

Voice: Amazon Polly Matthew, neural engine, American English. This stock synthetic narrator is used for the video; it is not an in-app voice feature.

## 0.6 seconds

When a volunteer cancels, finding a replacement takes more than an empty slot on a schedule. Meet Kind: a volunteer coordinator that helps small nonprofits keep their community covered.

## 16.5 seconds

This is Kind running on AWS. The food bank, volunteers, and shifts are fictional, so you can explore the full workflow.

## 27.0 seconds

Pantry preparation needs one more volunteer. Kind checks availability, qualifications, overlapping commitments, permission to receive invitations, and recent contact limits.

## 39.0 seconds

We select Strands and Amazon Bedrock. A private Lambda worker runs Nova Lite, using three bounded tools to inspect the shift, check eligible volunteers, and stage a draft.

## 58.0 seconds

The invitation is ready. Its time and location come from the saved shift. The agent cannot approve it or assign anyone.

## 69.0 seconds

The coordinator reviews the exact message and can edit it. Only their approval activates the volunteer response link.

## 80.0 seconds

Approval creates this individual response page. No email or text is sent by the demo. The link can be shared manually.

## 91.0 seconds

The volunteer sees their invitation and shift, then decides whether they can help. They do not get access to the full roster.

## 103.0 seconds

Acceptance checks eligibility and remaining capacity again, then saves the assignment. Repeating the response cannot overfill the shift.

## 115.0 seconds

Back in the coordinator workspace, the shift is covered. The roster and activity remain saved in Dynamo DB.

## 125.0 seconds

Preparation history shows what the Strands tools did. Model preparation, human approval, and the volunteer's response remain separate, visible steps.

## 137.0 seconds

Judges can restart the fictional sample for fresh future shifts. Confirmation explains the reset, and the daily AI allowance stays the same.

## 148.0 seconds

React and Fast API power the interface. A private Lambda worker runs Strands and Bedrock, while Dynamo DB protects the saved roster.

## 161.0 seconds

Kind is built for the Good Neighbor Agents track. The goal is less coordination work and more reliable coverage. It is a working sample, ready for feedback from nonprofit coordinators. A little coordination. A lot of good.

