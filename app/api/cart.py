from decimal import Decimal

from flask import request
from flask_restful import Resource
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from app.extensions import db
from app.models import CartItem, Product


def validate_cart_payload(data):
    if not isinstance(data, dict):
        return None, "Request body must be a JSON object"

    user_id = data.get("user_id")
    if isinstance(user_id, bool) or not isinstance(user_id, int) or user_id <= 0:
        return None, "User ID must be a positive integer"

    product_id = data.get("product_id")
    if (
        isinstance(product_id, bool)
        or not isinstance(product_id, int)
        or product_id <= 0
    ):
        return None, "Product ID must be a positive integer"

    quantity = data.get("quantity")
    if (
        isinstance(quantity, bool)
        or not isinstance(quantity, int)
        or quantity <= 0
    ):
        return None, "Quantity must be a positive integer"

    return {
        "user_id": user_id,
        "product_id": product_id,
        "quantity": quantity,
    }, None


class CartResource(Resource):
    def post(self):
        cart_data, validation_error = validate_cart_payload(
            request.get_json(silent=True)
        )
        if validation_error:
            return {"message": validation_error}, 400

        product = db.session.get(Product, cart_data["product_id"])
        if product is None:
            return {"message": "Product not found"}, 404

        cart_item = db.session.execute(
            db.select(CartItem).where(
                CartItem.user_id == cart_data["user_id"],
                CartItem.product_id == cart_data["product_id"],
            )
        ).scalar_one_or_none()

        new_quantity = cart_data["quantity"]
        status_code = 201
        if cart_item is not None:
            new_quantity += cart_item.quantity
            status_code = 200

        if new_quantity > product.stock:
            return {"message": "Requested quantity exceeds product stock"}, 400

        if cart_item is None:
            cart_item = CartItem(**cart_data)
            db.session.add(cart_item)
        else:
            cart_item.quantity = new_quantity

        try:
            db.session.commit()
        except OperationalError:
            db.session.rollback()
            return {"message": "Database unavailable"}, 503
        except SQLAlchemyError:
            db.session.rollback()
            return {"message": "Unable to add item to cart"}, 500

        return cart_item.to_dict(), status_code


class UserCartResource(Resource):
    def get(self, user_id):
        cart_items = db.session.execute(
            db.select(CartItem)
            .where(CartItem.user_id == user_id)
            .order_by(CartItem.id)
        ).scalars().all()

        total = sum(
            (item.product.price * item.quantity for item in cart_items),
            start=Decimal("0.00"),
        )

        return {
            "user_id": user_id,
            "items": [item.to_dict() for item in cart_items],
            "count": len(cart_items),
            "total": str(total),
        }, 200


class CartItemResource(Resource):
    def delete(self, user_id, product_id):
        cart_item = db.session.execute(
            db.select(CartItem).where(
                CartItem.user_id == user_id,
                CartItem.product_id == product_id,
            )
        ).scalar_one_or_none()

        if cart_item is None:
            return {"message": "Cart item not found"}, 404

        try:
            db.session.delete(cart_item)
            db.session.commit()
        except OperationalError:
            db.session.rollback()
            return {"message": "Database unavailable"}, 503
        except SQLAlchemyError:
            db.session.rollback()
            return {"message": "Unable to remove item from cart"}, 500

        return "", 204
