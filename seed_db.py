import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), "food.db")

schema = """
CREATE TABLE IF NOT EXISTS menu_items(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  description TEXT,
  price_cents INTEGER NOT NULL,
  image_url TEXT
);
"""
items = [
    (
        "Margherita Pizza",
        "Tomato, mozzarella, and basil on a crispy crust.",
        1199,
        "https://cdn.pixabay.com/photo/2017/12/09/08/18/pizza-3007395_1280.jpg"
    ),
    (
        "Veggie Burger",
        "Grilled patty with lettuce, tomato, and aioli.",
        999,
        "https://cdn.pixabay.com/photo/2016/03/05/19/02/hamburger-1238246_1280.jpg"
    ),
    (
        "Biryani",
        "Spicy Flavoured rice served with salna and raita.",
        1299,
        "https://images.unsplash.com/photo-1603133872878-684f208fb84b?auto=format&fit=crop&w=800&q=80"
    ),
    (
        "Caesar Salad",
        "Crisp romaine lettuce with parmesan and dressing.",
        849,
        "https://cdn.pixabay.com/photo/2015/04/08/13/13/salad-712665_1280.jpg"
    ),
    ("New York Cheesecake",
 "Creamy baked cheesecake with buttery biscuit crust.",
 749,
 "https://picsum.photos/seed/cheesecake/800/600")



]


with sqlite3.connect(DB_PATH) as db:
    db.executescript(schema)
    db.execute("DELETE FROM menu_items")
    db.executemany(
        "INSERT INTO menu_items(name, description, price_cents, image_url) VALUES (?, ?, ?, ?)",
        items,
    )
    db.commit()

print("✅ Seeded 5 menu items into food.db successfully!")
