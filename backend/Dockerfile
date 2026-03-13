FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

COPY config.json alembic.ini pyproject.toml uv.lock README.md ./
COPY alembic/ ./alembic/
COPY app/ ./app/
COPY scripts/ ./scripts/

RUN uv venv && uv pip install -e .

ENV PATH="/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    APP_ENV=production

COPY alembic.ini config.json .flake8 .python-version py.typed ./

EXPOSE 4444

COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["uv", "run", "service"]