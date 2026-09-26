from decimal import Decimal

from flask import current_app, request
from flask_restful import Resource
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import CartItem, Order, OrderItem


def validate_order_payload(data):
    if not isinstance(data, dict):
        return None, "Request body must be a JSON object"

    user_id = data.get("user_id")
    if isinstance(user_id, bool) or not isinstance(user_id, int) or user_id <= 0:
        return None, "User ID must be a positive integer"

    return user_id, None


class OrderListResource(Resource):
    def post(self):
        user_id, validation_error = validate_order_payload(
            request.get_json(silent=True)
        )
        if validation_error:
            return {"message": validation_error}, 400

        cart_items = db.session.execute(
            db.select(CartItem)
            .where(CartItem.user_id == user_id)
            .order_by(CartItem.id)
        ).scalars().all()

        if not cart_items:
            return {"message": "Cart is empty"}, 400

        for cart_item in cart_items:
            if cart_item.quantity > cart_item.product.stock:
                return {
                    "message": (
                        f"Insufficient stock for product {cart_item.product_id}"
                    )
                }, 400

        total_amount = sum(
            (
                cart_item.product.price * cart_item.quantity
                for cart_item in cart_items
            ),
            start=Decimal("0.00"),
        )
        order = Order(
            user_id=user_id,
            status="pending",
            total_amount=total_amount,
        )

        for cart_item in cart_items:
            order.items.append(
                OrderItem(
                    product_id=cart_item.product_id,
                    product_name=cart_item.product.name,
                    unit_price=cart_item.product.price,
                    quantity=cart_item.quantity,
                )
            )
            cart_item.product.stock -= cart_item.quantity
            db.session.delete(cart_item)

        try:
            db.session.add(order)
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            return {"message": "Unable to create order"}, 500

        current_app.extensions["project15_metrics"][
            "orders_created"
        ].inc()

        return order.to_dict(), 201


class OrderResource(Resource):
    def get(self, order_id):
        order = db.session.get(Order, order_id)
        if order is None:
            return {"message": "Order not found"}, 404

        return order.to_dict(), 200
