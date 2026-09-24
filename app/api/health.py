from flask_restful import Resource
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db


class ServiceInfoResource(Resource):
    def get(self):
        return {
            "name": "project15-app",
            "status": "running",
        }, 200


class LiveResource(Resource):
    def get(self):
        return {
            "status": "ok",
        }, 200


class ReadyResource(Resource):
    def get(self):
        try:
            db.session.execute(text("SELECT 1"))
        except SQLAlchemyError:
            return {
                "status": "not_ready",
                "database": "unavailable",
            }, 503

        return {
            "status": "ready",
            "database": "available",
        }, 200
