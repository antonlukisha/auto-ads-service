import os
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

from orjson import orjson

from app.core.config import get_config
from app.core.logging import get_logger, get_uvicorn_logger_config

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))


logger = get_logger(__name__)


def dev() -> None:
    """
    Run development server with auto-reload.
    """
    cfg = get_config()

    log_config = get_uvicorn_logger_config()
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".json", delete=False) as f:
        f.write(orjson.dumps(log_config, option=orjson.OPT_INDENT_2))
        log_config_path = f.name

    cmd = [
        "uvicorn",
        "app.main:create_app",
        "--factory",
        "--host",
        cfg.delivery.serve.host,
        "--port",
        str(cfg.delivery.serve.port),
        "--reload",
        "--reload-dir",
        "app",
        "--log-level",
        "info",
        "--log-config",
        log_config_path,
    ]

    process = None
    try:
        process = subprocess.Popen(cmd)
        process.wait()

    except KeyboardInterrupt:
        if process.poll() is None:
            if os.name == "nt":
                process.terminate()
            else:
                process.send_signal(signal.SIGINT)

            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        logger.info("Server stopped by user")


def migrate() -> None:
    """
    Run database migrations.
    """
    subprocess.run(["alembic", "upgrade", "head"])


def makemigrations(message: str) -> None:
    """
    Create a new migration.
    """
    subprocess.run(["alembic", "revision", "--autogenerate", "-m", message])


def lint() -> None:
    """
    Run linters.
    """
    subprocess.run(["black", "app", "scripts"])
    subprocess.run(["isort", "app", "scripts"])
    subprocess.run(["flake8", "app", "scripts"])
    subprocess.run(["mypy", "app"])


def downgrade(revision: str = "-1") -> None:
    """
    Rollback database to a specific revision.

    :param revision: The revision to roll back to (default: -1)
    :type revision: str
    :return: nothing
    :rtype: None
    """
    subprocess.run(["alembic", "downgrade", revision])


def show_history() -> None:
    """
    Show migration history.
    """
    subprocess.run(["alembic", "history"])


def current() -> None:
    """
    Show current migration revision.
    """
    subprocess.run(["alembic", "current"])
