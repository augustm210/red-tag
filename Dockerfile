FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

COPY pyproject.toml README.md ./
COPY red_tag_agent ./red_tag_agent
COPY services ./services

RUN pip install --no-cache-dir .

USER 65532:65532

CMD ["sh", "-c", "uvicorn services.api.main:app --host 0.0.0.0 --port ${PORT}"]
