import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = (
        os.getenv("DATABASE_URL")
        or (
            Path("/var/run/secrets/project15/DATABASE_URL").read_text().strip()
            if Path("/var/run/secrets/project15/DATABASE_URL").is_file()
            else None
        )
        or "sqlite:///project15.db"
    )
    if os.getenv("KUBERNETES_SERVICE_HOST") and SQLALCHEMY_DATABASE_URI == "sqlite:///project15.db":
        raise RuntimeError("DATABASE_URL is required when running in Kubernetes")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    SECURITY_REPORTS_DIR = os.getenv(
        "SECURITY_REPORTS_DIR",
        "security-reports",
    )
