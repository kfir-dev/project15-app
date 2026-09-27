from flask import Blueprint
from flask_restful import Api
from sqlalchemy.exc import OperationalError

from app.api.cart import CartItemResource, CartResource, UserCartResource
from app.api.health import LiveResource, ReadyResource, ServiceInfoResource
from app.api.orders import OrderListResource, OrderResource
from app.api.products import ProductListResource, ProductResource
from app.api.security_reports import SbomResource, ScanReportResource
from app.extensions import db


class ProjectApi(Api):
    def handle_error(self, error):
        if isinstance(error, OperationalError):
            db.session.rollback()
            return self.make_response({"message": "Database unavailable"}, 503)

        return super().handle_error(error)


api_blueprint = Blueprint("api", __name__)
api = ProjectApi(api_blueprint)

api.add_resource(ServiceInfoResource, "/")
api.add_resource(LiveResource, "/health/live")
api.add_resource(ReadyResource, "/health/ready")
api.add_resource(ProductListResource, "/api/products")
api.add_resource(ProductResource, "/api/products/<int:product_id>")
api.add_resource(CartResource, "/api/cart")
api.add_resource(UserCartResource, "/api/cart/<int:user_id>")
api.add_resource(
    CartItemResource,
    "/api/cart/<int:user_id>/item/<int:product_id>",
)
api.add_resource(OrderListResource, "/api/orders")
api.add_resource(OrderResource, "/api/orders/<int:order_id>")
api.add_resource(SbomResource, "/api/security/sbom")
api.add_resource(ScanReportResource, "/api/security/scan-report")
