# Kind AWS preflight

Historical review snapshot. The user subsequently approved deployment, both stacks completed, and the live workflow passed. See `deployment.json` for current evidence. The unexecuted statuses below describe the state at this preflight checkpoint.

Verified September 10, 2026 Pacific time through the reconnected AWS Core connector.

## Account and service readiness

Account: `114599789754`. Target region: `us-west-2`.

STS identity, Lambda account settings and CloudFormation stack listing succeeded. No Kind stacks existed before this preflight. Lambda reported 1,000 total concurrent executions and 992 unreserved, which leaves room for the planned single reserved worker execution. This check does not reserve capacity.

CloudFormation ValidateTemplate accepted both `infra/artifacts.json` and `infra/template.json`. The application template requires CAPABILITY_IAM for its two runtime roles. Bedrock reported Amazon Nova Lite agreement, entitlement and region availability as AVAILABLE and authorization as AUTHORIZED. This is account readiness, not verification of the future worker role.

## Unexecuted artifact change set

Stack: `kind-artifacts`

Change set: `kind-artifact-review-20260911`

Change set ARN: `arn:aws:cloudformation:us-west-2:114599789754:changeSet/kind-artifact-review-20260911/98bb42cf-a47a-4672-a9bb-9174ae4d6633`

Status: CREATE_COMPLETE. Execution status: AVAILABLE.

The reviewed changes are Add `Artifacts` (AWS::S3::Bucket) and Add `TlsOnly` (AWS::S3::BucketPolicy). DescribeEvents returned no validation errors. The stack shell is REVIEW_IN_PROGRESS; the bucket and policy have not been provisioned. No application resources, deployment credentials or live endpoint have been created.

## Scope for deployment approval

Execute the reviewed artifact change set, upload the already tested package, then create, inspect and execute the application change set using the reviewed template only if its checks pass and its changes match this scope:

1. One private encrypted S3 artifact bucket with public access blocked and TLS required.
2. One HTTPS API Gateway endpoint serving Kind, two Lambda functions, and two scoped runtime IAM roles.
3. One encrypted DynamoDB sample workspace table, two log groups and one encrypted failure queue.
4. A randomly generated coordinator access code and an independent session signing key, handled outside source and public output.
5. The default limit of 20 admitted live AI runs per UTC day, one active AI job and one reserved worker execution. Individual runs retain the five model call and 900 output token limits.

These resources introduce metered AWS charges. The AI admission limit is not a hard dollar cap. The bucket, table and queue are retained on stack deletion and require separate reviewed cleanup. Existing project resources are outside this deployment scope. No public GitHub visibility change, Devpost publication action or final contest submission is included.

The package SHA256 remains `810f330ec05094e64e3da4edd64775b101de77937b84ebbcfb3c0582c09d88e6`. See `aws-deployment.md` for the full design and `infra-validation.json` for local template validation.
