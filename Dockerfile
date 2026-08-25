FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
WORKDIR /app

# All environment variables in one layer
ENV UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_NO_PROGRESS=1 \
    PYTHONUNBUFFERED=1 \
    DOCKER_CONTAINER=1 \
    AWS_REGION=us-east-1 \
    AWS_DEFAULT_REGION=us-east-1

ENV BEDROCK_AGENTCORE_MEMORY_ID="hr_agent_mem-AdoG9PFkTC"


ENV BEDROCK_AGENTCORE_MEMORY_NAME="hr_agent_mem"

# Inference profile ARNs (from cdk-outputs.json + list-inference-profiles)
ENV INFERENCE_PROFILE_ARN_CLAUDE_HAIKU="arn:aws:bedrock:us-east-1:869520403603:inference-profile/us.anthropic.claude-haiku-4-5-20251001-v1:0"
ENV INFERENCE_PROFILE_ARN_NOVA_PRO="arn:aws:bedrock:us-east-1:869520403603:inference-profile/us.amazon.nova-pro-v1:0"
ENV INFERENCE_PROFILE_ARN_NOVA_LITE="arn:aws:bedrock:us-east-1:869520403603:inference-profile/us.amazon.nova-lite-v1:0"
ENV INFERENCE_PROFILE_ARN_NOVA_2_LITE="arn:aws:bedrock:us-east-1:869520403603:inference-profile/us.amazon.nova-2-lite-v1:0"

# Bedrock Knowledge Base for retrieve tool
ENV KNOWLEDGE_BASE_ID="ITMRYVQRJD"




COPY agent/requirements.txt agent/requirements.txt
# Install from requirements file
RUN uv pip install -r agent/requirements.txt




RUN uv pip install aws-opentelemetry-distro==0.12.2


# Signal that this is running in Docker for host binding logic
ENV DOCKER_CONTAINER=1

# Create non-root user
RUN useradd -m -u 1000 bedrock_agentcore
USER bedrock_agentcore

EXPOSE 9000
EXPOSE 8000
EXPOSE 8080

# Copy entire project (respecting .dockerignore)
COPY . .

# Use the full module path

CMD ["opentelemetry-instrument", "python", "-m", "agent.agent"]
