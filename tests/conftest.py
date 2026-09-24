import pytest

from app import create_app
from app.config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


@pytest.fixture()
def client():
    app = create_app(TestConfig)

    with app.test_client() as test_client:
        yield test_client
