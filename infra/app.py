#!/usr/bin/env python3
"""CDK app entrypoint - stack unico para o chatbot de RH."""

from __future__ import annotations

import os

import aws_cdk as cdk

from infra.stack import ChatbotRhStack

app = cdk.App()

ChatbotRhStack(
    app,
    "ChatbotRhStack",
    env=cdk.Environment(
        account=os.environ.get("CDK_DEFAULT_ACCOUNT"),
        region="us-east-1",  # ALWAYS us-east-1 (project.md Mandated)
    ),
    description="Chatbot de RH: S3 bucket, Bedrock KB e IAM roles. AgentCore Runtime via CLI/console.",
)

app.synth()
