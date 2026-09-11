# Kind AWS deployment plan

Status: deployed and verified after explicit user approval. Both `kind-artifacts` and `kind-demo` reached CREATE_COMPLETE in `us-west-2`. The actual HTTPS workflow completed live Bedrock preparation, coordinator approval and volunteer acceptance, with the roster saved in DynamoDB. See `deployment.json` and `live-verification.json` for evidence. `aws-preflight.md` records the earlier review and approval scope.

Target: the connected AWS account, region `us-west-2`. Use the AWS Core connector for deployment. The connector connection does not give the standalone local app SDK credentials, and no credentials need to be exported from it.

## Deployed resource design

1. An artifact stack from `infra/artifacts.json`: a private S3 bucket with public access blocked, encryption, versioning and a policy requiring TLS.
2. An application stack from `infra/template.json`: an HTTPS API Gateway endpoint, a web Lambda, a private agent Lambda, two scoped runtime IAM roles, a DynamoDB table, two log groups with seven day retention, and an encrypted queue for failed worker deliveries.
3. A random coordinator access code and an independent random cookie signing key. Only the access code digest goes into the backend. Sensitive CloudFormation parameters use NoEcho. Runtime environment values remain accessible to appropriately authorized AWS administrators. Do not put these values in source, a URL, command output, GitHub, or Devpost.

Suggested stack names: `kind-artifacts` and `kind-demo`. Check for name collisions before creating them. Deployment should only create or update the named Kind stacks. Existing projects are outside this scope.

## Demo behavior

The frontend is served by the web Lambda through the API. The coordinator signs in with the demo access code. Volunteer response links remain scoped bearer links and can be opened without coordinator access. All organization and volunteer records are fictional.

The web function can read and write Kind's table and invoke only Kind's worker. The worker can read and write the same table and invoke only Amazon Nova Lite in the selected region. It cannot approve invitations or contact volunteers through its agent tools.

AI preparation returns a job identifier immediately. The browser polls the job result while the worker performs the Strands loop. This avoids the HTTP API integration timeout. AWS documents the timeout behavior in its [HTTP API integration reference](https://docs.aws.amazon.com/cli/latest/reference/apigatewayv2/create-integration.html).

Default limits are 20 admitted live AI runs per UTC day, five model calls per run, and 900 output tokens per model call. A persisted job claim prevents duplicate worker deliveries from executing a second loop. Failed attempts consume their admission allowance. Rules mode remains available after the daily live limit is exhausted. API throttling is configured at three requests per second with a burst of six. These are usage controls, not a guaranteed dollar cap.

The worker has one reserved concurrent execution and a five minute function timeout. Its asynchronous event delivery allows no function error retries and keeps undelivered events for at most sixty seconds. Delivery failures go to the encrypted queue. The UI reports unfinished jobs after their lease expires. See [AWS asynchronous invocation configuration](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-lambda-eventinvokeconfig.html).

## Costs and retained data

Deployment introduces metered charges for Lambda execution, API requests, DynamoDB reads and writes, S3 storage, logs, queue operations and Bedrock tokens. There is no always running EC2 instance or NAT gateway in these templates. No fixed cost ceiling is claimed. Authentication limits who can initiate paid AI runs; ordinary public requests can still consume hosting resources.

The artifact bucket, table and failure queue are retained if their stacks are deleted. This protects data from accidental stack deletion but means those resources need separate reviewed cleanup and can continue to incur storage charges. The queue retains failed events for fourteen days. The workspace has a conservative document size guard and is intended for the bounded sample roster.

## Rebuild the deployment package

Install `uv` into the development environment, run `pnpm build`, then run:

```powershell
python scripts/package_lambda.py --output ../kind-deployment/kind-demo.zip
```

Choose a new output filename if a package already exists. The builder evaluates Python dependencies for Linux even on Windows, bundles the frontend and backend, and writes a SHA256 manifest. It never logs in to AWS or deploys anything. The package excludes local databases, tests, access codes and environment files. `infra/requirements-lambda-lock.txt` records the resolved Linux dependencies.

The corresponding runtime smoke command uses the official Lambda Python image with the output directory mounted read only:

```sh
docker run --rm --entrypoint python -e KIND_HOSTED=1 -e AWS_EC2_METADATA_DISABLED=true -v /absolute/path/to/outputs:/build:ro public.ecr.aws/lambda/python:3.12 /build/kind/scripts/smoke_lambda_package.py /build/kind-deployment/kind-demo.zip
```

## Deployment sequence completed after approval

1. Local validation completed: cfn-lint 1.56.3 returned no findings for either template; cfn-guard 3.2.1 passed all twelve applicable selected checks. Ten checks were inapplicable to one template. Both cloud change sets passed validation, matched the reviewed additions and were executed after approval.
2. Recheck the connected account and region, confirm the stack names are unused or belong to Kind, and confirm the reserved concurrency allocation is available. Verify the specific Nova Lite model can be invoked with the intended role policy.
3. Create the artifact stack. Upload the package through a short lived presigned S3 upload URL to an immutable key such as `kind/<package-sha256>.zip`.
4. Generate and preserve the demo access code and signing key in an ignored local deployment directory. Supply the digest and signing key as NoEcho parameters. Keep the access code out of tool output and public submission materials.
5. Create and inspect the application change set with CAPABILITY_IAM. Execute only the reviewed Kind changes after approval.
6. Verify the resulting HTTPS endpoint, access restrictions, live AI job, approval, volunteer response, conditional roster update, persisted state, and visible failure behavior against the actual deployed resources.
7. Record the exact deployed source commit and package digest. Add the verified demo URL and judge access instructions to the draft. Public repository visibility and final Devpost submission remain separate publication decisions.

The hosted demo is verified through the actual cloud endpoint. The repository remains private and the hackathon entry has not been submitted. No real nonprofit operation is claimed.
