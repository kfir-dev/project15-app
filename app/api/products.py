from decimal import Decimal, InvalidOperation

from flask import request
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Product


def validate_product_payload(data):
    if not isinstance(data, dict):
        return None, "Request body must be a JSON object"

    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        return None, "Product name is required"
    if len(name.strip()) > 120:
        return None, "Product name must not exceed 120 characters"

    description = data.get("description")
    if description is not None and not isinstance(description, str):
        return None, "Product description must be a string"
    if isinstance(description, str) and len(description) > 500:
        return None, "Product description must not exceed 500 characters"

    try:
        price = Decimal(str(data.get("price")))
    except (InvalidOperation, TypeError, ValueError):
        return None, "Product price must be a valid number"
    if price <= 0:
        return None, "Product price must be greater than zero"

    stock = data.get("stock", 0)
    if isinstance(stock, bool) or not isinstance(stock, int):
        return None, "Product stock must be an integer"
    if stock < 0:
        return None, "Product stock must not be negative"

    return {
        "name": name.strip(),
        "description": description,
        "price": price,
        "stock": stock,
    }, None


class ProductListResource(Resource):
    def get(self):
        products = db.session.execute(
            db.select(Product).order_by(Product.id)
        ).scalars().all()

        return {
            "products": [product.to_dict() for product in products],
            "count": len(products),
        }, 200

    def post(self):
        product_data, validation_error = validate_product_payload(
            request.get_json(silent=True)
        )
        if validation_error:
            return {"message": validation_error}, 400

        product = Product(**product_data)

        try:
            db.session.add(product)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            return {"message": "Unable to create product"}, 500

        return product.to_dict(), 201


class ProductResource(Resource):
    def put(self, product_id):
        product = db.session.get(Product, product_id)
        if product is None:
            return {"message": "Product not found"}, 404

        product_data, validation_error = validate_product_payload(
            request.get_json(silent=True)
        )
        if validation_error:
            return {"message": validation_error}, 400

        product.name = product_data["name"]
        product.description = product_data["description"]
        product.price = product_data["price"]
        product.stock = product_data["stock"]

        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            return {"message": "Unable to update product"}, 500

        return product.to_dict(), 200

    def delete(self, product_id):
        product = db.session.get(Product, product_id)
        if product is None:
            return {"message": "Product not found"}, 404

        try:
            db.session.delete(product)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            return {"message": "Unable to delete product"}, 500

        return "", 204
