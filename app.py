import os, sqlite3, stripe
from flask import Flask, jsonify, render_template, request, url_for
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
PUBLISHABLE_KEY = os.environ.get("STRIPE_PUBLISHABLE_KEY")
DB_PATH = os.path.join(os.path.dirname(__file__), "food.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')



@app.route("/menu")
def menu(): return render_template("menu.html", pk=PUBLISHABLE_KEY)

@app.route("/success")
def success(): return render_template("success.html")

@app.route("/api/menu")
def api_menu():
    with get_db() as db:
        rows = db.execute(
            "SELECT id,name,description,price_cents,image_url FROM menu_items"
        ).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    data = request.get_json(force=True)
    requested = {int(i["id"]): int(i.get("quantity", 1)) for i in data.get("items", [])}
    with get_db() as db:
        q_marks = ",".join("?" * len(requested))
        rows = db.execute(
            f"SELECT id,name,description,price_cents FROM menu_items WHERE id IN ({q_marks})",
            tuple(requested.keys()),
        ).fetchall()

    line_items = [{
        "quantity": requested[r["id"]],
        "price_data": {
            "currency": "usd",
            "unit_amount": r["price_cents"],
            "product_data": {"name": r["name"], "description": r["description"]},
        },
    } for r in rows]

    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=line_items,
        success_url=url_for("success", _external=True) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=url_for("menu", _external=True),
    )
    return jsonify({"checkout_url": session.url})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8002)

