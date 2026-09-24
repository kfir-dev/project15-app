from flask import Blueprint
from flask_restful import Api

from app.api.health import LiveResource, ReadyResource, ServiceInfoResource


api_blueprint = Blueprint("api", __name__)
api = Api(api_blueprint)

api.add_resource(ServiceInfoResource, "/")
api.add_resource(LiveResource, "/health/live")
api.add_resource(ReadyResource, "/health/ready")
