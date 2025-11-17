import random
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///zomato_clone.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Restaurant(db.Model):
    __tablename__ = "restaurants"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    cuisine = db.Column(db.String(80), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)

    menu_items = db.relationship("MenuItem", back_populates="restaurant", lazy=True)


class MenuItem(db.Model):
    __tablename__ = "menu_items"

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey("restaurants.id"), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    price = db.Column(db.Float, nullable=False)
    is_veg = db.Column(db.Boolean, default=True)
    category = db.Column(db.String(50), nullable=True)  # e.g. Starter, Main Course, Dessert

    restaurant = db.relationship("Restaurant", back_populates="menu_items")


class UserProfile(db.Model):
    __tablename__ = "user_profiles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)

    addresses = db.relationship("Address", back_populates="profile", cascade="all, delete-orphan")


class Address(db.Model):
    __tablename__ = "addresses"

    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("user_profiles.id"), nullable=False)
    label = db.Column(db.String(80), nullable=True)
    address_line = db.Column(db.String(255), nullable=False)

    profile = db.relationship("UserProfile", back_populates="addresses")


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    customer_name = db.Column(db.String(120), nullable=False)
    delivery_address = db.Column(db.String(255), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(20), nullable=False, default="Cash")
    status = db.Column(db.String(50), default="PLACED", nullable=False)

    items = db.relationship("OrderItem", back_populates="order", lazy=True)


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey("menu_items.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price_each = db.Column(db.Float, nullable=False)

    order = db.relationship("Order", back_populates="items")
    menu_item = db.relationship("MenuItem")


def get_cart():
    """Return cart from session as {menu_item_id: quantity}."""
    return session.get("cart", {})


def save_cart(cart):
    session["cart"] = cart
    session.modified = True


def get_cart_count():
    cart = get_cart()
    return sum(cart.values())


@app.context_processor
def inject_cart_meta():
    return {"cart_count": get_cart_count()}


def get_or_create_profile():
    profile = UserProfile.query.first()
    if not profile:
        profile = UserProfile()
        db.session.add(profile)
        db.session.commit()
    return profile


@app.route("/")
def home():
    restaurants = Restaurant.query.all()
    return render_template("home.html", restaurants=restaurants)


@app.route("/restaurant/<int:restaurant_id>")
def restaurant_detail(restaurant_id: int):
    restaurant = Restaurant.query.get_or_404(restaurant_id)

    veg_filter = request.args.get("veg", "all")  # all, veg, nonveg
    category_filter = request.args.get("category", "all")
    price_filter = request.args.get("price", "all")  # all, lt200, bt200_400, gt400
    limit_filter = request.args.get("limit", "all")

    query = MenuItem.query.filter_by(restaurant_id=restaurant.id)

    if veg_filter == "veg":
        query = query.filter_by(is_veg=True)
    elif veg_filter == "nonveg":
        query = query.filter_by(is_veg=False)

    if category_filter != "all":
        query = query.filter_by(category=category_filter)

    if price_filter == "lt200":
        query = query.filter(MenuItem.price < 200)
    elif price_filter == "bt200_400":
        query = query.filter(MenuItem.price.between(200, 400))
    elif price_filter == "gt400":
        query = query.filter(MenuItem.price > 400)

    if limit_filter.isdigit():
        items = query.limit(int(limit_filter)).all()
    else:
        items = query.all()

    # Distinct categories for this restaurant to populate filter dropdown
    categories = (
        db.session.query(MenuItem.category)
        .filter(
            MenuItem.restaurant_id == restaurant.id,
            MenuItem.category.isnot(None),
        )
        .distinct()
        .all()
    )
    categories = [c[0] for c in categories]

    current_cart = get_cart()
    cart_item_ids = set(current_cart.keys())
    cart_quantities = {int(k): v for k, v in current_cart.items()}

    return render_template(
        "restaurant.html",
        restaurant=restaurant,
        items=items,
        categories=categories,
        veg_filter=veg_filter,
        category_filter=category_filter,
        price_filter=price_filter,
        limit_filter=limit_filter,
        limit_options=["5", "10", "20", "all"],
        cart_item_ids=cart_item_ids,
        cart_quantities=cart_quantities,
    )


@app.route("/cart/add", methods=["POST"])
def add_to_cart():
    menu_item_id = request.form.get("menu_item_id")
    if not menu_item_id:
        return redirect(request.referrer or url_for("home"))

    try:
        menu_item_id = int(menu_item_id)
    except ValueError:
        return redirect(request.referrer or url_for("home"))

    menu_item = MenuItem.query.get_or_404(menu_item_id)

    try:
        quantity = int(request.form.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1
    quantity = max(1, quantity)

    mode = request.form.get("mode", "add")
    cart = get_cart()
    key = str(menu_item_id)

    if mode == "update":
        if quantity <= 0:
            cart.pop(key, None)
            flash(f"Removed {menu_item.name} from cart.", "success")
        else:
            cart[key] = quantity
            flash(f"Updated {menu_item.name} to {quantity}.", "success")
    else:
        cart[key] = cart.get(key, 0) + quantity
        flash(f"Added {quantity} × {menu_item.name} to cart.", "success")

    save_cart(cart)
    return redirect(request.referrer or url_for("home"))


@app.route("/cart")
def view_cart():
    cart = get_cart()
    item_ids = [int(i) for i in cart.keys()]
    items = MenuItem.query.filter(MenuItem.id.in_(item_ids)).all() if item_ids else []

    detailed_items = []
    total_amount = 0.0
    for item in items:
        qty = cart.get(str(item.id), 0)
        line_total = item.price * qty
        total_amount += line_total
        detailed_items.append(
            {
                "item": item,
                "quantity": qty,
                "line_total": line_total,
            }
        )

    return render_template(
        "cart.html", items=detailed_items, total_amount=total_amount
    )


@app.route("/cart/update", methods=["POST"])
def update_cart():
    cart = get_cart()
    for key, value in request.form.items():
        if not key.startswith("qty_"):
            continue
        item_id = key.split("_", 1)[1]
        try:
            qty = int(value)
        except ValueError:
            qty = cart.get(item_id, 1)
        if qty <= 0:
            cart.pop(item_id, None)
        else:
            cart[item_id] = qty

    save_cart(cart)
    flash("Cart updated.", "success")
    return redirect(url_for("view_cart"))


@app.route("/cart/empty", methods=["POST"])
def empty_cart():
    """Clear all items from the cart."""
    save_cart({})
    flash("Cart emptied.", "success")
    return redirect(url_for("view_cart"))


@app.route("/cart/remove/<int:item_id>", methods=["POST"])
def remove_cart_item(item_id: int):
    """Remove a single menu item from the cart."""
    cart = get_cart()
    cart.pop(str(item_id), None)
    save_cart(cart)
    flash("Item removed from cart.", "success")
    return redirect(url_for("view_cart"))


@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    cart = get_cart()
    if not cart:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("home"))

    item_ids = [int(i) for i in cart.keys()]
    items = MenuItem.query.filter(MenuItem.id.in_(item_ids)).all()

    profile = UserProfile.query.first()
    saved_addresses = profile.addresses if profile else []

    detailed_items = []
    total_amount = 0.0
    for item in items:
        qty = cart.get(str(item.id), 0)
        line_total = item.price * qty
        total_amount += line_total
        detailed_items.append(
            {
                "item": item,
                "quantity": qty,
                "line_total": line_total,
            }
        )

    if request.method == "POST":
        customer_name = request.form.get("customer_name")
        delivery_address = request.form.get("delivery_address")
        payment_method = request.form.get("payment_method")

        if not all([customer_name, delivery_address, payment_method]):
            flash("Please provide your name, address and payment method.", "danger")
            return redirect(url_for("checkout"))

        order = Order(
            customer_name=customer_name,
            delivery_address=delivery_address,
            total_amount=total_amount,
            payment_method=payment_method,
            status="PLACED",
        )
        db.session.add(order)
        db.session.flush()

        for item_info in detailed_items:
            item = item_info["item"]
            qty = item_info["quantity"]
            order_item = OrderItem(
                order_id=order.id,
                menu_item_id=item.id,
                quantity=qty,
                price_each=item.price,
            )
            db.session.add(order_item)

        db.session.commit()
        save_cart({})

        flash("Order placed successfully!", "success")
        return redirect(url_for("order_confirmation", order_id=order.id))

    return render_template(
        "checkout.html",
        items=detailed_items,
        total_amount=total_amount,
        saved_addresses=saved_addresses,
    )


@app.route("/order/<int:order_id>")
def order_confirmation(order_id: int):
    order = Order.query.get_or_404(order_id)
    return render_template("order_confirmation.html", order=order)


@app.route("/profile", methods=["GET", "POST"])
def profile():
    profile = get_or_create_profile()

    if request.method == "POST":
        profile.name = request.form.get("name") or None
        profile.email = request.form.get("email") or None
        profile.phone = request.form.get("phone") or None
        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("profile"))

    return render_template("profile.html", profile=profile)


@app.route("/profile/address", methods=["POST"])
def add_address():
    profile = get_or_create_profile()
    label = request.form.get("label")
    address_line = request.form.get("address_line")

    if not address_line:
        flash("Address cannot be empty.", "danger")
        return redirect(url_for("profile"))

    address = Address(profile_id=profile.id, label=label or None, address_line=address_line)
    db.session.add(address)
    db.session.commit()
    flash("Address added.", "success")
    return redirect(url_for("profile"))


@app.route("/profile/address/<int:address_id>/delete", methods=["POST"])
def delete_address(address_id: int):
    address = Address.query.get_or_404(address_id)
    db.session.delete(address)
    db.session.commit()
    flash("Address removed.", "success")
    return redirect(url_for("profile"))


@app.cli.command("init-db")
def init_db_command():
    """Initialize the database tables with many sample restaurants and menu items."""
    db.drop_all()
    db.create_all()

    # Create 30 restaurants with varied cuisines and cover images
    cuisine_types = [
        "Indian",
        "Chinese",
        "Italian",
        "North Indian",
        "South Indian",
        "Fast Food",
        "Biryani",
        "Desserts",
    ]

    restaurant_images = [
        "https://images.pexels.com/photos/958545/pexels-photo-958545.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/54455/cook-food-kitchen-eat-54455.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/262978/pexels-photo-262978.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/70497/pexels-photo-70497.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/315755/pexels-photo-315755.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/1640774/pexels-photo-1640774.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/1438672/pexels-photo-1438672.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/376464/pexels-photo-376464.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/1095550/pexels-photo-1095550.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/2233729/pexels-photo-2233729.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/1234530/pexels-photo-1234530.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/1640775/pexels-photo-1640775.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/410648/pexels-photo-410648.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/461198/pexels-photo-461198.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/291528/pexels-photo-291528.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/236781/pexels-photo-236781.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/761854/pexels-photo-761854.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/1640773/pexels-photo-1640773.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/1410235/pexels-photo-1410235.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/357756/pexels-photo-357756.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/1583884/pexels-photo-1583884.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/3682836/pexels-photo-3682836.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/3642690/pexels-photo-3642690.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/3298647/pexels-photo-3298647.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/374052/pexels-photo-374052.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/2290070/pexels-photo-2290070.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/3184192/pexels-photo-3184192.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/1640771/pexels-photo-1640771.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/776538/pexels-photo-776538.jpeg?auto=compress&cs=tinysrgb&w=800",
        "https://images.pexels.com/photos/1309598/pexels-photo-1309598.jpeg?auto=compress&cs=tinysrgb&w=800",
    ]

    restaurant_data = [
        ("Spice Route", "Slow-cooked curries, freshly ground masalas, and fluffy naan straight from the tandoor.", "Indian"),
        ("Urban Tadka", "Modern Indian fusion paired with smoky grills and bold street flavors.", "Indian"),
        ("Curry Leaf", "South Indian comfort plates with coconut-rich gravies and filter coffee.", "South Indian"),
        ("Dragon Wok", "Stir-fried classics with sizzling woks, fiery schezwan, and delicate dim sum.", "Chinese"),
        ("Noodle House", "Hand-pulled noodles, brothy soups, and crispy spring rolls made to order.", "Chinese"),
        ("Pizza Palace", "Wood-fired pizzas topped with buffalo mozzarella and heritage tomatoes.", "Italian"),
        ("Pasta Point", "Freshly rolled pasta tossed in rich sauces and sprinkled with Parmigiano.", "Italian"),
        ("Burger Hub", "Stacked burgers, brioche buns, triple-cooked fries, and signature sauces.", "Fast Food"),
        ("Biryani Blues", "Hyderabadi handi biryanis layered with fragrant basmati and saffron.", "Biryani"),
        ("Bombay Bites", "Iconic Mumbai street snacks from vada pav to tangy bhel puri.", "Fast Food"),
        ("Southern Spice", "Banana leaf spreads, gunpowder podis, and tangy rasam shots.", "South Indian"),
        ("Idli Express", "Soft idlis, crispy medu vadas, and piping hot sambar all day long.", "South Indian"),
        ("Dosa Junction", "Paper-thin dosas stuffed with masala, cheese, and fiery chutneys.", "South Indian"),
        ("Chaat Corner", "Crisp puris, sweet curd, and spice-packed chutneys in every bite.", "Fast Food"),
        ("Sweet Tooth", "Artisanal desserts, chocolate ganache jars, and molten lava cakes.", "Desserts"),
        ("Dessert Den", "Cheesecakes, tiramisu cups, and flambéed desserts for every occasion.", "Desserts"),
        ("Tandoori Nights", "Char-grilled kebabs, smoky tikka platters, and buttery garlic naan.", "North Indian"),
        ("Grill & Chill", "BBQ platters, seared steaks, and refreshing mocktails on the side.", "Fast Food"),
        ("Masala Street", "Fusion chaats, stuffed kulchas, and kulfi falooda for a nostalgic feast.", "North Indian"),
        ("Royal Thali", "Grand Rajasthani and Gujarati thalis with endless katoris and sweets.", "North Indian"),
        ("Punjabi Zaika", "Hearty makhni gravies, stuffed parathas, and lassi served in matkas.", "North Indian"),
        ("Taste of China", "Classic Hakka noodles, momos, and chilli chicken with smoky wok hei.", "Chinese"),
        ("Mama Mia Pizza", "Thin-crust pizzas, garlic knots, and sun-dried tomato bruschetta.", "Italian"),
        ("Wrap ‘n Roll", "Kathi rolls, shawarmas, and stuffed pita pockets on the go.", "Fast Food"),
        ("Kebab Factory", "Seekh, shami, and galouti kebabs marinated in secret spice blends.", "North Indian"),
        ("Oriental Bowl", "Rice bowls layered with teriyaki, tofu, and crunchy veggies.", "Chinese"),
        ("Falafel House", "Mediterranean platters with hummus, falafel, and pickled sides.", "Fast Food"),
        ("Veggie Garden", "Farm-to-table salads, smoothie bowls, and wholesome grain plates.", "Desserts"),
        ("Midnight Cravings", "Late-night munchies from loaded fries to chocolate brownies.", "Fast Food"),
    ]

    restaurants = []
    for i, (name, description, cuisine) in enumerate(restaurant_data):
        image_url = restaurant_images[i % len(restaurant_images)]
        r = Restaurant(
            name=name,
            description=description,
            cuisine=cuisine,
            image_url=image_url,
        )
        restaurants.append(r)

    db.session.add_all(restaurants)
    db.session.flush()

    # Menu templates per cuisine to ensure variety
    menu_templates = {
        "Indian": [
            ("Butter Chicken", False, "Main Course"),
            ("Paneer Butter Masala", True, "Main Course"),
            ("Dal Tadka", True, "Main Course"),
            ("Chicken Tikka", False, "Starter"),
            ("Veg Seekh Kebab", True, "Starter"),
            ("Garlic Naan", True, "Sides"),
            ("Jeera Rice", True, "Sides"),
            ("Gulab Jamun", True, "Dessert"),
            ("Bhindi Fry", True, "Main Course"),
            ("Malai Kofta", True, "Main Course"),
            ("Fish Amritsari", False, "Starter"),
            ("Kulfi Falooda", True, "Dessert"),
        ],
        "South Indian": [
            ("Masala Dosa", True, "Breakfast"),
            ("Onion Uttapam", True, "Breakfast"),
            ("Idli Sambar", True, "Breakfast"),
            ("Chettinad Chicken", False, "Main Course"),
            ("Vegetable Korma", True, "Main Course"),
            ("Lemon Rice", True, "Sides"),
            ("Filter Coffee", True, "Beverage"),
            ("Podi Idli", True, "Snacks"),
            ("Ghee Roast Dosa", True, "Breakfast"),
            ("Mysore Pak", True, "Dessert"),
        ],
        "North Indian": [
            ("Amritsari Chole", True, "Main Course"),
            ("Lassi", True, "Beverage"),
            ("Chicken Butter Garlic", False, "Main Course"),
            ("Paneer Tikka Roll", True, "Snacks"),
            ("Dal Makhani", True, "Main Course"),
            ("Stuffed Kulcha", True, "Sides"),
            ("Phirni", True, "Dessert"),
            ("Rajma Masala", True, "Main Course"),
            ("Kadai Chicken", False, "Main Course"),
            ("Aloo Tikki", True, "Starter"),
        ],
        "Chinese": [
            ("Veg Hakka Noodles", True, "Main Course"),
            ("Chicken Manchurian", False, "Main Course"),
            ("Spring Rolls", True, "Starter"),
            ("Schezwan Fried Rice", True, "Main Course"),
            ("Kung Pao Chicken", False, "Main Course"),
            ("Veg Momos", True, "Snacks"),
            ("Hot & Sour Soup", True, "Starter"),
            ("Chilli Paneer", True, "Starter"),
            ("Lemon Coriander Soup", True, "Starter"),
            ("Dragon Chicken", False, "Starter"),
        ],
        "Italian": [
            ("Margherita Pizza", True, "Main Course"),
            ("Pepperoni Pizza", False, "Main Course"),
            ("Four Cheese Pasta", True, "Main Course"),
            ("Pesto Penne", True, "Main Course"),
            ("Tiramisu", True, "Dessert"),
            ("Bruschetta", True, "Starter"),
            ("Minestrone Soup", True, "Starter"),
            ("Risotto Funghi", True, "Main Course"),
            ("Arrabbiata Pasta", True, "Main Course"),
            ("Chocolate Mousse", True, "Dessert"),
        ],
        "Fast Food": [
            ("Crispy Chicken Burger", False, "Snacks"),
            ("Veggie Delight Burger", True, "Snacks"),
            ("Loaded Nachos", True, "Starter"),
            ("Cheesy Fries", True, "Snacks"),
            ("BBQ Wings", False, "Starter"),
            ("Chocolate Shake", True, "Beverage"),
            ("Club Sandwich", True, "Snacks"),
            ("Chicken Popcorn", False, "Snacks"),
            ("Peri Peri Fries", True, "Snacks"),
            ("Paneer Wrap", True, "Snacks"),
        ],
        "Biryani": [
            ("Hyderabadi Chicken Biryani", False, "Main Course"),
            ("Lucknowi Mutton Biryani", False, "Main Course"),
            ("Veg Dum Biryani", True, "Main Course"),
            ("Egg Biryani", False, "Main Course"),
            ("Raita", True, "Sides"),
            ("Double Ka Meetha", True, "Dessert"),
            ("Keema Biryani", False, "Main Course"),
            ("Paneer Biryani", True, "Main Course"),
            ("Mirchi Ka Salan", True, "Sides"),
        ],
        "Desserts": [
            ("Chocolate Lava Cake", True, "Dessert"),
            ("Blueberry Cheesecake", True, "Dessert"),
            ("Red Velvet Jar", True, "Dessert"),
            ("Ice Cream Sundae", True, "Dessert"),
            ("Fruit Tart", True, "Dessert"),
            ("Banoffee Pie", True, "Dessert"),
            ("Macarons", True, "Dessert"),
            ("Chocolate Brownie", True, "Dessert"),
            ("Panna Cotta", True, "Dessert"),
        ],
    }

    default_templates = [
        ("Chef Special Curry", False, "Main Course"),
        ("Garden Salad", True, "Starter"),
        ("House Dessert", True, "Dessert"),
    ]

    menu_items = []
    for rest in restaurants:
        templates = menu_templates.get(rest.cuisine, default_templates)
        for idx in range(20):
            name, is_veg, category = random.choice(templates)
            price = random.randint(150, 550)
            menu_items.append(
                MenuItem(
                    restaurant_id=rest.id,
                    name=f"{name} #{idx+1}",
                    description=f"Chef's take on {name.lower()} at {rest.name}.",
                    price=price,
                    is_veg=is_veg,
                    category=category,
                )
            )

    db.session.add_all(menu_items)
    db.session.commit()

    # Ensure default profile exists
    get_or_create_profile()

    print("Database initialized with 30 restaurants, 50 menu items, and default profile.")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    # For public access, use host='0.0.0.0' to bind to all network interfaces
    # For production, set debug=False and use a proper WSGI server (like Gunicorn)
    app.run(host='0.0.0.0', port=5000, debug=True)


