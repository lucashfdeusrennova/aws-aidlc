**Collaborator:** aidlc-developer-agent

# Unit Test Instructions - infra

## Sources

- [tp] `team.md § Testing Posture` - Infraestrutura CDK validada por `cdk synth`, sem pytest sobre o stack no escopo mvp.

## How to validate

```bash
cdk synth       # gera CloudFormation, valida sintaxe + tipos
```

Inspecionar o template gerado em `cdk.out/ChatbotRhStack.template.json`:

- Grep `"Resource": "\*"` no bloco Policies do agente -> zero hits (NFR5.2.1).
- Verificar SSE-S3 no BucketEncryption do S3 bucket.
- Verificar que os 2 inference profile ARNs sao referenciados por
  bedrock:InvokeModel*.

## No pytest tests

CDK validation e via `cdk synth`, nao pytest (team.md).

## Assumptions & Open Questions

None.
