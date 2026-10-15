import re


# Small in-memory dataset for learning. Replace this with a real database in a real system.
ORDERS = {
    "ORD-1001": {
        "status": "In transit",
        "estimated_delivery": "2026-10-16",
        "item": "Wireless headphones",
    },
    "ORD-1002": {
        "status": "Delivered",
        "estimated_delivery": "2026-10-10",
        "item": "Mechanical keyboard",
    },
    "ORD-1003": {
        "status": "Processing",
        "estimated_delivery": "Not available yet",
        "item": "USB-C hub",
    },
}


def find_order_id(message: str) -> str | None:
    match = re.search(r"\bORD-\d{4}\b", message.upper())
    return match.group(0) if match else None


def lookup_order(message: str) -> str:
    order_id = find_order_id(message)
    if not order_id:
        return (
            "No order ID was found in the customer's message. "
            "Ask the customer to provide an order ID such as ORD-1001."
        )

    order = ORDERS.get(order_id)
    if not order:
        return f"No order was found for {order_id}. Check the order ID and try again."

    return (
        f"Order ID: {order_id}\n"
        f"Item: {order['item']}\n"
        f"Status: {order['status']}\n"
        f"Estimated delivery: {order['estimated_delivery']}"
    )
