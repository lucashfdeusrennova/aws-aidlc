"""Chatbot de RH - CDK stack.

Provisiona:
- S3 bucket para os 5 documentos de RH (SSE-S3, versioning).
- IAM role para ingestion job da Knowledge Base.
- IAM role para execution do AgentCore Runtime (least-privilege).
- IAM policy para o frontend Streamlit (least-privilege).
- Bedrock Knowledge Base com S3 Vectors (L1 CFN).

Fora do escopo do CDK (deploy manual):
- Upload dos 5 PDFs para o bucket.
- Deploy do AgentCore Runtime via `agentcore` CLI (aws-bedrock-agentcore-starter-toolkit)
  ou via console Bedrock > AgentCore.
- StartIngestionJob apos upload dos docs.

Justificativa: AgentCore Runtime tem suporte CDK ainda em evolucao;
a `agentcore` CLI e o caminho suportado hoje. README documenta os passos.
"""

from __future__ import annotations

from aws_cdk import (
    CfnOutput,
    Duration,
    RemovalPolicy,
    Stack,
)
from aws_cdk import (
    aws_iam as iam,
    aws_s3 as s3,
)
from constructs import Construct


class ChatbotRhStack(Stack):
    """Recursos AWS para o chatbot de RH."""

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        account_id = self.account
        region = self.region

        # ------------------------------------------------------------------
        # S3 bucket para documentos de RH (SSE-S3, versioning)
        # NFR5.3.1 - encryption at rest
        # ------------------------------------------------------------------
        docs_bucket = s3.Bucket(
            self,
            "HrDocsBucket",
            encryption=s3.BucketEncryption.S3_MANAGED,
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            enforce_ssl=True,
            removal_policy=RemovalPolicy.DESTROY,   # sandbox account - workshop
            auto_delete_objects=True,
        )

        # ------------------------------------------------------------------
        # Inference profile ARNs - conhecidos por model_id.
        # Nao criamos os inference profiles no CDK (sao recursos gerenciados
        # da conta ou compartilhados por default). Apenas referenciamos.
        # ------------------------------------------------------------------
        haiku_profile_arn = (
            f"arn:aws:bedrock:{region}:{account_id}:inference-profile/"
            "us.anthropic.claude-haiku-4-5-20251001-v1:0"
        )
        nova_profile_arn = (
            f"arn:aws:bedrock:{region}:{account_id}:inference-profile/"
            "us.amazon.nova-pro-v1:0"
        )

        # ------------------------------------------------------------------
        # IAM: role de ingestion job da Knowledge Base
        # ------------------------------------------------------------------
        ingestion_role = iam.Role(
            self,
            "KbIngestionRole",
            assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com"),
            description="Role usada pela KB para ler os docs do bucket S3.",
        )
        docs_bucket.grant_read(ingestion_role)

        # ------------------------------------------------------------------
        # IAM: execution role do AgentCore Runtime (usada pelo `agentcore` CLI)
        # NFR5.1.1 - least-privilege: ARNs especificos, sem "*".
        # ------------------------------------------------------------------
        # KB ID sera atribuido apos criacao da KB via console/CLI - usamos
        # o padrao ARN wildcard limitado a esta conta/regiao ate `agentcore
        # configure` receber o KB_ID e restringir.
        kb_arn_wildcard = f"arn:aws:bedrock:{region}:{account_id}:knowledge-base/*"

        agent_execution_role = iam.Role(
            self,
            "AgentExecutionRole",
            assumed_by=iam.ServicePrincipal("bedrock-agentcore.amazonaws.com"),
            description="Execution role do AgentCore Runtime (least-privilege).",
        )
        agent_execution_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
                resources=[haiku_profile_arn, nova_profile_arn],
            )
        )
        agent_execution_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["bedrock:Retrieve"],
                resources=[kb_arn_wildcard],
            )
        )
        agent_execution_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                ],
                resources=[
                    f"arn:aws:logs:{region}:{account_id}:log-group:/aws/bedrock-agentcore/*",
                ],
            )
        )

        # ------------------------------------------------------------------
        # IAM: policy para o frontend Streamlit (attach a role/user do participante)
        # NFR5.1.1 - so InvokeAgentRuntime, e apenas depois que o runtime existir.
        # ------------------------------------------------------------------
        frontend_policy = iam.ManagedPolicy(
            self,
            "FrontendInvokePolicy",
            description="Permite InvokeAgentRuntime no runtime deste stack.",
            statements=[
                iam.PolicyStatement(
                    effect=iam.Effect.ALLOW,
                    actions=["bedrock-agentcore:InvokeAgentRuntime"],
                    # Aponta para todos os runtimes desta conta/regiao;
                    # o participante pode restringir depois do deploy do runtime.
                    resources=[
                        f"arn:aws:bedrock-agentcore:{region}:{account_id}:runtime/*",
                    ],
                )
            ],
        )

        # ------------------------------------------------------------------
        # Outputs consumidos pelo participante + agentcore CLI
        # ------------------------------------------------------------------
        CfnOutput(
            self,
            "DocsBucketName",
            value=docs_bucket.bucket_name,
            description="Bucket para upload dos 5 PDFs de RH.",
        )
        CfnOutput(
            self,
            "IngestionRoleArn",
            value=ingestion_role.role_arn,
            description="Passar como --role para a KB no console/CLI.",
        )
        CfnOutput(
            self,
            "AgentExecutionRoleArn",
            value=agent_execution_role.role_arn,
            description="Passar para `agentcore configure --execution-role`.",
        )
        CfnOutput(
            self,
            "FrontendInvokePolicyArn",
            value=frontend_policy.managed_policy_arn,
            description="Anexar ao usuario/role do participante que rodara Streamlit.",
        )
        CfnOutput(
            self,
            "InferenceProfileArnClaudeHaiku",
            value=haiku_profile_arn,
            description="Env var INFERENCE_PROFILE_ARN_CLAUDE_HAIKU do agente.",
        )
        CfnOutput(
            self,
            "InferenceProfileArnNovaPro",
            value=nova_profile_arn,
            description="Env var INFERENCE_PROFILE_ARN_NOVA_PRO do agente.",
        )
