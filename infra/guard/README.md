# Template validation rules

The five service rules in this directory are unmodified copies from the [AWS Guard rules registry](https://github.com/aws-cloudformation/aws-guard-rules-registry/tree/7f7340c26ae5d5e8874651dbffeb12e0e9f505b6/rules/aws), commit `7f7340c26ae5d5e8874651dbffeb12e0e9f505b6`. They check S3 public access blocking, S3 encryption, the TLS policy and DynamoDB encryption. The upstream Apache 2.0 license is included in `LICENSE`.

`kind.guard` adds project specific checks for retained data, queue encryption, hosted mode, sensitive parameters, AI admission controls and the private worker boundary.

These are selected template checks, not an exhaustive security audit or verification of actual AWS runtime permissions. Rules for absent resource types correctly report SKIP. There are no rule suppressions in the Kind templates.

Validated using cfn-guard 3.2.1 from the [official release](https://github.com/aws-cloudformation/cloudformation-guard/releases/tag/3.2.1).
