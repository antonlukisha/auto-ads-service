#!/bin/bash
set -e

wait_for_postgres() {
    for i in {1..30}; do
        if pg_isready -h postgres -U postgres > /dev/null 2>&1; then
            return 0
        fi
        sleep 2
    done
    exit 1
}

if ! command -v pg_isready &> /dev/null; then
    apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*
fi

wait_for_postgres

uv run alembic upgrade head

exec "$@"