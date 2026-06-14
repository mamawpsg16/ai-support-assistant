"""
seed.py — fill the database with fake sample data for testing.

Run it with:  python seed.py

It DROPS all tables and recreates them fresh each time, so you always get a clean,
predictable dataset (5 customers, 5 products, 10 orders, 3 subscriptions). Because we
reset first, ids are always 1..5 — so we can refer to customers/products by real id.

This is a standalone script (not part of the web app). It opens its own DB session,
inserts rows, commits, and prints a summary.
"""

from backend.database import Base, SessionLocal, engine

# Import models so Base.metadata knows all tables (same side-effect import as main.py).
from backend.models import Customer, Order, OrderStatus, Product, Subscription, SubscriptionStatus


def reset_tables():
    """Drop every table then recreate them — a clean slate."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def seed():
    reset_tables()

    # SessionLocal() opens one DB session for this script (same factory main.py uses).
    db = SessionLocal()
    try:
        # --- 5 customers (will get ids 1..5) ------------------------------------
        customers = [
            Customer(name="Alice Johnson", email="alice@example.com"),
            Customer(name="Bob Smith", email="bob@example.com"),
            Customer(name="Carla Reyes", email="carla@example.com"),
            Customer(name="David Lee", email="david@example.com"),
            Customer(name="Esther Cruz", email="esther@example.com"),
        ]
        db.add_all(customers)   # stage all 5 inserts
        db.commit()             # save -> each customer now has an id (1..5)

        # --- 5 products (ids 1..5, with fake Stripe price ids for Phase 2) -------
        products = [
            Product(name="Wireless Mouse", description="Ergonomic 2.4GHz mouse",
                    price=25.00, stripe_price_id="price_demo_001"),
            Product(name="Mechanical Keyboard", description="RGB hot-swap keyboard",
                    price=80.00, stripe_price_id="price_demo_002"),
            Product(name="USB-C Hub", description="7-in-1 multiport adapter",
                    price=45.50, stripe_price_id="price_demo_003"),
            Product(name="1080p Webcam", description="Auto-focus streaming webcam",
                    price=60.00, stripe_price_id="price_demo_004"),
            Product(name="Laptop Stand", description="Aluminium adjustable stand",
                    price=35.00, stripe_price_id="price_demo_005"),
        ]
        db.add_all(products)
        db.commit()

        # Look up a product's price by its id, so we can copy it onto an order's total.
        # Example result: {1: 25.0, 2: 80.0, 3: 45.5, 4: 60.0, 5: 35.0}
        product_price = {}
        for p in products:
            product_price[p.id] = p.price

        # --- 10 orders across mixed statuses ------------------------------------
        # Each row is (customer_id, product_id, status) using REAL ids (1..5).
        # Read it like a small table: who ordered what, and in what state.
        order_specs = [
            (1, 1, OrderStatus.pending),
            (1, 3, OrderStatus.paid),
            (2, 2, OrderStatus.shipped),
            (2, 4, OrderStatus.delivered),
            (3, 5, OrderStatus.delivered),
            (3, 1, OrderStatus.refunded),
            (4, 2, OrderStatus.paid),
            (4, 3, OrderStatus.pending),
            (5, 4, OrderStatus.shipped),
            (5, 5, OrderStatus.delivered),
        ]

        # Build one Order object per row, then add them all.
        orders = []
        for customer_id, product_id, order_status in order_specs:
            new_order = Order(
                customer_id=customer_id,
                product_id=product_id,
                status=order_status,
                total=product_price[product_id],   # total = that product's price
            )
            orders.append(new_order)

        db.add_all(orders)
        db.commit()

        # --- 3 subscriptions (mixed statuses) -----------------------------------
        subscriptions = [
            Subscription(customer_id=1, plan_name="Pro",
                         status=SubscriptionStatus.active),
            Subscription(customer_id=2, plan_name="Basic",
                         status=SubscriptionStatus.past_due),
            Subscription(customer_id=4, plan_name="Pro",
                         status=SubscriptionStatus.canceled),
        ]
        db.add_all(subscriptions)
        db.commit()

        # --- Summary -------------------------------------------------------------
        print("Database seeded successfully:")
        print(f"  customers     : {db.query(Customer).count()}")
        print(f"  products      : {db.query(Product).count()}")
        print(f"  orders        : {db.query(Order).count()}")
        print(f"  subscriptions : {db.query(Subscription).count()}")
    finally:
        db.close()   # always close the session, success or error


# This block runs only when you execute `python seed.py` directly (not on import).
if __name__ == "__main__":
    seed()
