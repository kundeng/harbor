# Harbor v2 Python runner
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VENV_PATH=/opt/venv

# System deps minimally for docker CLI in container contexts (optional)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl git \
 && rm -rf /var/lib/apt/lists/*

# Create venv
RUN python -m venv ${VENV_PATH}
ENV PATH="${VENV_PATH}/bin:${PATH}"

WORKDIR /workspace
COPY requirements.txt /workspace/requirements.txt
RUN pip install --no-cache-dir -r /workspace/requirements.txt

# Default command prints help; Justfile will override
CMD ["python", "-m", "lib.cli", "--help"]
