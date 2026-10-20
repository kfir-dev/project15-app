from flask import Flask

from app.api import api_blueprint
from app.config import Config
from app.extensions import db, migrate
from app.metrics import init_metrics


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(api_blueprint)
    init_metrics(app)

    @app.after_request
    def set_content_type_options(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    return app
