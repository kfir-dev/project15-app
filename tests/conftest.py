import pytest

from app import create_app
from app.config import Config
from app.extensions import db


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


@pytest.fixture()
def client(tmp_path):
    app = create_app(TestConfig)
    app.config["SECURITY_REPORTS_DIR"] = str(tmp_path / "security-reports")

    with app.app_context():
        db.create_all()

        with app.test_client() as test_client:
            yield test_client

        db.session.remove()
        db.drop_all()
