import sqlite3

conn = sqlite3.connect("orders.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    product TEXT,
    size TEXT
)
""")

conn.commit()


def save_order(user_id: int, product: str, size: str):
    cursor.execute(
        "INSERT INTO orders (user_id, product, size) VALUES (?, ?, ?)",
        (user_id, product, size)
    )
    conn.commit()
