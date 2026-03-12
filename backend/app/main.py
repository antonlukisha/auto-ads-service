import asyncio
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import router
from app.core.config import Config, get_config
from app.core.database import db
from app.core.logging import get_logger, get_uvicorn_logger_config, setup_logging
from app.models.schemas import HealthResponse
from app.scraper.worker import scraper_worker

sys.path.insert(0, str(Path(__file__).parent.parent))

setup_logging()
logger = get_logger(__name__)

config: Config | None = None


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator:
    """
    Lifespan context manager for startup and shutdown events.
    """
    global config

    config = get_config()
    logger.info("Starting up...")

    try:
        await db.initialize(config.postgres_dsn)
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise Exception(f"Failed to connect to database: {e}")
    else:
        logger.info("Database connected")
        logger.info(f"dsn:{db.dsn}")
    scraper_worker.start()

    yield

    logger.info("Shutting down...")
    scraper_worker.stop()
    await db.close()
    logger.info("Database disconnected")


def create_app(cfg: Config | None = None) -> FastAPI | None:
    """
    Create FastAPI application.

    :param cfg: Application configuration
    :type cfg: Config
    :return: FastAPI application
    :rtype: FastAPI | None
    """
    global config

    if cfg is None:
        try:
            cfg = get_config()
            if cfg is None:
                logger.error("Config.load returned None")
                return None
        except FileNotFoundError:
            logger.error("config.json not found")
            return None
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return None

    config = cfg

    app = FastAPI(
        title="Auto ADS Service",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    origins = [origin.strip() for origin in cfg.delivery.cors.allow_origins.split(",")]

    app.add_middleware(
        CORSMiddleware,  # type: ignore
        allow_origins=origins,
        allow_credentials=cfg.delivery.cors.allow_credentials,
        allow_methods=["*"],
        allow_headers=[h.strip() for h in cfg.delivery.cors.allow_headers.split(",")],
        expose_headers=(
            [h.strip() for h in cfg.delivery.cors.expose_headers.split(",")]
            if cfg.delivery.cors.expose_headers
            else []
        ),
    )

    app.include_router(router, prefix="/api")

    @app.get("/")
    async def root():
        """
        Root endpoint.
        """
        return {
            "service": "auto-ads-service-backend",
            "version": "1.0.0",
            "status": "running",
            "docs": "/api/docs",
        }

    @app.get("/health", response_model=HealthResponse)
    async def health_check():
        """
        Health check endpoint.
        """
        return HealthResponse()

    return app


async def run_server(cfg: Config) -> None:
    """
    Run the server.

    :param cfg: Application configuration
    :type cfg: Config
    :return: nothing
    :return: None
    """
    app = create_app(cfg)

    if app is None:
        return
    uvicorn_config = uvicorn.Config(
        app=app,
        host=cfg.delivery.serve.host,
        port=cfg.delivery.serve.port,
        log_level="info",
        log_config=get_uvicorn_logger_config(),
        proxy_headers=True,
        forwarded_allow_ips="*",
    )

    server = uvicorn.Server(uvicorn_config)

    logger.info(f"Server starting on http://{cfg.delivery.serve.host}:{cfg.delivery.serve.port}")
    logger.info(
        f"API Documentation: http://{cfg.delivery.serve.host}:{cfg.delivery.serve.port}/api/docs"
    )
    try:
        await server.serve()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        logger.info("Server shutdown complete")


async def main() -> None:
    """
    Main entry point.
    """
    try:
        cfg = get_config()

        await run_server(cfg)
    except FileNotFoundError:
        logger.error("config.json not found")
        sys.exit(1)

    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)


def run() -> None:
    """
    Synchronous entry point for running the app.
    """

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run()
