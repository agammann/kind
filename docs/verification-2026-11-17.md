# Local readiness review, November 17, 2026

This review used a fresh checkout and a separate fictional SQLite workspace. It did not replace the ordinary local workspace or reset the shared AWS sample.

## Setup and automated checks

Python 3.12.14, Node 24.22.1 and pnpm 11.19.0 were exercised on Windows. The Python test requirements were installed with the repository constraints; `pip check` passed. All 55 tests passed, with the expected SQLite skip for a DynamoDB conditional-write case and one Starlette test-client deprecation warning. DynamoDB tests use Moto, and the real Strands loop tests use a scripted model; neither establishes a current cloud or paid-model result.

The TypeScript 7.0.2 and Vite 6.4.6 production build passed, and the JavaScript dependency audit reported zero findings. Vite was updated from 6.4.5 to the patched 6.4.6 line for [GHSA-p4f5-76q4-ffq7](https://github.com/vitejs/vite/security/advisories/GHSA-p4f5-76q4-ffq7). The advisory concerns a network-exposed development server; Kind's development script binds to loopback and production serves built assets. No exploit or production compromise is claimed. The setup guide now names the CI runtime and pinned package manager instead of unqualified Python/Node/pnpm requirements.

## Actual browser workflow

The rules-mode invitation, coordinator approval, volunteer acceptance and saved Saturday roster were exercised through the actual interface without a model call. Recording Maya's cancellation reopened the shift and recommended Jordan. This exposed a presentation defect: the internal declined marker used to prevent immediate re-invitation appeared as a second invitation.

The display now excludes records whose source is `cancellation`. After reloading the same workspace, the genuine Maya invitation remained Cancelled and Jordan remained recommended, while the internal marker was no longer shown as a response. Pantry preparation still showed Aisha's genuine Declined invitation and Maya's Needs approval draft. The backend marker, eligibility, contact accounting, approvals and response rules are unchanged. The manual browser review supplied the rendered before/after check; no duplicate implementation-mirroring test was added.

The owned Uvicorn process then completed application shutdown and restarted against the exact same database. An actual browser reload retained Saturday's one-of-two roster, Maya's Cancelled invitation, Jordan's two prior contacts, and Pantry's genuine decline and reviewable draft. Browser errors were empty. The server was shut down again after this check; the original workspace and separate integrity-checked SQLite backups were retained privately.

## Fresh Linux package

The repository's package builder produced a new Linux Python 3.12 x86_64 package from the current Linux dependency lock, backend and built interface. Its SHA256 is `b379410dac355f0c9061c39708e671c60dea8798e7062416f9e69f7d905b395e` (29,885,371 compressed bytes). All eight server files and three frontend files match the working source/build; the package contains no local database or environment file. Windows checkout line endings are retained in server payloads; their immutable Git equivalents differ only by CRLF/LF normalization.

The actual ZIP passed the existing smoke test in the pinned official Lambda Python 3.12 image with `--network none`. Imports, rules draft, authentication, API Gateway v2 adapter, persisted roster, frontend and scripted Strands guard cases passed. This establishes an offline package execution, not an AWS-deployed Lambda or a live Bedrock call. The earlier pre-fix package was preserved separately.

## Delivery boundaries

The fresh AWS Core connection preflight returned UNAUTHORIZED and required reauthentication before any AWS API call ran. No upload, change set, stack update, secret retrieval, private hosted login, shared-roster mutation or paid model call occurred in this review. The October 2 deployment and live-model records remain historical evidence; they do not identify this local package as deployed.

Kind has no GitHub artifact-release publisher or established version-tag flow. The private frontend package version is not being repurposed as an invented release. Source changes use the existing reviewed pull-request and CI process; a later authorized AWS update must preserve the current stacks, access parameters, fictional workspace and usage allowance. See [AWS deployment guidance](aws-deployment.md).
