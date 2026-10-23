FROM python:3.14-slim@sha256:0514bc76712d64f8bb48adcb95b1ab0d88c69fee95d62fe4c18ee948bee9b1e1

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_ROOT_USER_ACTION=ignore \
    RUFF_NO_CACHE=true

WORKDIR /app

COPY requirements-dev.txt .
RUN pip install --require-hashes -r requirements-dev.txt \
    && useradd --create-home --uid 10001 app

COPY . .

USER app

CMD ["python", "main.py", "2"]
