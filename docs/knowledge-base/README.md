# Knowledge Base - Documentos de RH

Coloque aqui os 5 documentos de RH antes do upload para o bucket S3:

- `employee_handbook.pdf` - Manual do funcionario
- `leave_policy.pdf` - Politica de licenca e ferias
- `onboarding_checklist.pdf` - Processo de onboarding
- `performance_review_guidelines.pdf` - Diretrizes de avaliacao
- `public_holidays.csv` - Calendario de feriados

**IMPORTANTE (project.md Forbidden)**: nunca coloque documentos com dados
individuais de colaboradores (contracheques, avaliacoes nominais, historico
disciplinar) neste diretorio. Documentos com PII sao vetor de vazamento por
prompt injection e sao explicitamente proibidos pela politica CC-1/CC-2.

Upload:

```bash
aws s3 cp docs/knowledge-base/ s3://<DocsBucketName>/ --recursive --region us-east-1
```
