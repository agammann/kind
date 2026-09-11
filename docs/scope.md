# Kind — first working version

Approved direction: Good Neighbor Agents, helping one small nonprofit keep volunteer shifts covered. The user chose the name Kind and authorized building in Codex and creating the project with Devpost and GitHub.

## Complete workflow
1. View persistent shifts, volunteer records, and coverage gaps.
2. Check eligibility against full-shift availability, required qualifications, overlapping assignments, and recent contact load.
3. Use a Strands agent with bounded tools to inspect a gap and prepare a replacement invitation. Keep an explicitly labeled rules-only option for offline testing.
4. Coordinator reviews the exact invitation before approving it. The agent cannot approve, send, or assign.
5. Volunteer opens a unique invitation page and accepts or declines.
6. Acceptance atomically assigns an eligible volunteer if capacity remains. Declines reopen the decision; duplicate acceptances never overfill a shift.
7. Show an activity history and preserve state across restarts.

## Initial boundaries
Single organization, local preview, clearly labeled fictional records, no external email/SMS sending. Approval creates an in-app invitation that can be shared manually. No production deployment or final contest submission during the local build. Live model testing depends on AWS sign-in and Bedrock access.

## Design
White canvas, deep cobalt #234BD8, ink #172647, pale neutral #F4F6FA. Left navigation, open shift list, right recommendation panel, accessible controls, responsive stacking on small screens. App-native actions first.

## Verification
Exercise persisted approval and response state, ineligible candidates, repeat actions, conflicting assignments, concurrent acceptances, stale invitations, and API role boundaries. Build the frontend and verify the end-to-end local workflow. Report model-backed checks separately from offline checks.
