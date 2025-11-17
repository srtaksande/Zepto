## Zomato-Style Food Delivery App (Flask)

This is a simple **food delivery web application** similar to Swiggy/Zomato, built with **Python (Flask)** and **SQLite**.

### Features

- List restaurants with cuisine, description, and cover image.
- View restaurant menu items (veg/non-veg, description, price).
- Add items to cart and adjust quantities.
- Checkout with customer name and delivery address.
- Store orders and ordered items in a SQL database.

### Setup

1. Open Command Prompt and go to the project:

```bash
cd "C:\Users\Hitachi\Desktop\Cursor Projects\Zomato"
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

If `pip` fails, try:

```bash
py -m pip install -r requirements.txt
```

3. Initialize the database with sample data:

```bash
flask --app app init-db
```

This will create `zomato_clone.db` and seed a few restaurants and menu items.

### Run the Application

```bash
cd "C:\Users\Hitachi\Desktop\Cursor Projects\Zomato"
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.

### Main Pages

- `/` – Restaurant listing (home).
- `/restaurant/<id>` – Restaurant details and menu.
- `/cart` – View/update cart.
- `/checkout` – Place order.
- `/order/<id>` – Order confirmation page.


