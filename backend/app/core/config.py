import os
from pathlib import Path

import orjson
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

load_dotenv()


class CorsConfig(BaseModel):
    allow_origins: str = Field(default="*", min_length=1, description="Allowed origins for CORS")
    allow_headers: str = Field(default="*", min_length=1, description="Allowed headers for CORS")
    expose_headers: str = Field(default="", description="Exposed headers for CORS")
    allow_credentials: bool = Field(default=False, description="Allow credentials in CORS")


class ServerConfig(BaseModel):
    proxy_header: str = Field(
        default="X-Real-IP", min_length=1, description="Proxy header to trust"
    )
    read_timeout_seconds: int = Field(
        default=30, gt=0, le=300, description="Read timeout in seconds"
    )
    write_timeout_seconds: int = Field(
        default=30, gt=0, le=300, description="Write timeout in seconds"
    )
    disable_startup_message: bool = Field(default=False, description="Disable startup message")


class ServeConfig(BaseModel):
    address: str = Field(
        default=":4444", pattern=r"^[a-zA-Z0-9\.\-]*:\d+$", description="Server address (host:port)"
    )

    @property
    def host(self) -> str:
        return self.address.split(":")[0]

    @property
    def port(self) -> int:
        parts = self.address.split(":")
        return int(parts[1]) if len(parts) > 1 else 5560


class JWTConfig(BaseModel):
    secret_key: str = Field(default_factory=lambda: os.getenv("JWT_SECRET_KEY", ""), min_length=32)
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=75, gt=0)


class DeliveryConfig(BaseModel):
    server: ServerConfig = Field(default_factory=ServerConfig)
    cors: CorsConfig = Field(default_factory=CorsConfig)
    serve: ServeConfig = Field(default_factory=ServeConfig)


class Config(BaseSettings):
    shutdown_timeout_seconds: int = Field(
        default=30, gt=0, description="Shutdown timeout in seconds"
    )
    postgres_dsn: str = Field(
        default_factory=lambda: os.getenv("POSTGRES_DSN", ""),
        min_length=1,
        pattern=r"^postgres(ql)?://.*$",
        description="PostgreSQL connection string",
    )

    jwt: JWTConfig = Field(default_factory=JWTConfig, description="JWT configuration")

    delivery: DeliveryConfig = Field(
        default_factory=DeliveryConfig, description="Delivery configuration"
    )

    @classmethod
    def load(cls, path: str) -> "Config":
        """
        Load configuration from JSON file and environment variables.

        :param path: Path to JSON file
        :type path: str
        :return: Config object
        :rtype: Config
        """
        config_path = Path(path)
        if config_path.exists():
            with open(config_path, "rb") as f:
                try:
                    data = orjson.loads(f.read())
                except orjson.JSONDecodeError as e:
                    raise ValueError(f"Invalid JSON in config file: {e}")

            if "Delivery" in data:
                delivery_data = data["Delivery"]
                data["delivery"] = {
                    "server": delivery_data.get("Server", {}),
                    "cors": delivery_data.get("Cors", {}),
                    "serve": delivery_data.get("Serve", {}),
                }
                del data["Delivery"]

            if "ShutdownTimeoutSeconds" in data:
                data["shutdown_timeout_seconds"] = data["ShutdownTimeoutSeconds"]
                del data["ShutdownTimeoutSeconds"]

            if "JWT" in data:
                jwt = data["JWT"]
                data["jwt"] = {
                    "algorithm": jwt.get("Algorithm", "HS256"),
                    "access_token_expire_minutes": jwt.get("AccessTokenExpireMinutes", 75),
                }
                del data["JWT"]

            if "delivery" in data and "server" in data["delivery"]:
                server = data["delivery"]["server"]
                if "ReadTimeoutSeconds" in server:
                    server["read_timeout_seconds"] = server["ReadTimeoutSeconds"]
                    del server["ReadTimeoutSeconds"]
                if "WriteTimeoutSeconds" in server:
                    server["write_timeout_seconds"] = server["WriteTimeoutSeconds"]
                    del server["WriteTimeoutSeconds"]
                if "ProxyHeader" in server:
                    server["proxy_header"] = server["ProxyHeader"]
                    del server["ProxyHeader"]
                if "DisableStartupMessage" in server:
                    server["disable_startup_message"] = server["DisableStartupMessage"]
                    del server["DisableStartupMessage"]

            if "delivery" in data and "cors" in data["delivery"]:
                cors = data["delivery"]["cors"]
                if "AllowOrigins" in cors:
                    cors["allow_origins"] = cors["AllowOrigins"]
                    del cors["AllowOrigins"]
                if "AllowHeaders" in cors:
                    cors["allow_headers"] = cors["AllowHeaders"]
                    del cors["AllowHeaders"]
                if "ExposeHeaders" in cors:
                    cors["expose_headers"] = cors["ExposeHeaders"]
                    del cors["ExposeHeaders"]
                if "AllowCredentials" in cors:
                    cors["allow_credentials"] = cors["AllowCredentials"]
                    del cors["AllowCredentials"]

            if "delivery" in data and "serve" in data["delivery"]:
                serve = data["delivery"]["serve"]
                if "Address" in serve:
                    serve["address"] = serve["Address"]
                    del serve["Address"]

            try:
                return cls(**data)
            except Exception as e:
                raise ValueError(f"Invalid configuration: {e}")

        return cls()


config: Config | None = None


def get_config() -> Config:
    global config
    if config is None:
        config = Config.load("config.json")
    return config
