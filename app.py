from email.policy import default
from types import NoneType
from flask import Flask, render_template, request, redirect, url_for, make_response, render_template_string, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from json import dumps as js_dumps
import ast
import re

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

root = "http://localhost:80/"

class Item(db.Model):
    id = db.Column(db.String(16), unique=True, nullable=False, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    desc = db.Column(db.String(400), unique=False, nullable=False)
    img_url = db.Column(db.String(400), unique=False, nullable=False)
    price = db.Column(db.String(12), unique=False, nullable=False)
    
class Deal(db.Model):
    code = db.Column(db.String(16), unique=True, nullable=False, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    desc = db.Column(db.String(400), unique=False, nullable=False)
    public = db.Column(db.Boolean, default=False, nullable=False)
    deal = db.Column(db.String(12), unique=False, nullable=False)
    
class User(db.Model):
    username = db.Column(db.String(24), unique=True, nullable=False)
    firstname = db.Column(db.String(40), unique=False, nullable=False)
    lastname = db.Column(db.String(40), unique=False, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False, primary_key=True)
    billing_address = db.Column(db.String(80), nullable=True)
    shipping_address = db.Column(db.String(80), nullable=True)
    balance = db.Column(db.Integer, unique=False, nullable=False, default=0)
    blocked = db.Column(db.String(1), unique=False, nullable=False, default=0)
    password_hash = db.Column(db.String(60), unique=False, nullable=False)
    permission_level = db.Column(db.Integer, unique=False, nullable=False, default=0)


deals = [
    ["deal1", "1% off with code:'deal1'"],
    ["deal2", "2% off with code:'deal2'"]
]

# --- HOME ---
@app.route("/home")
def home_redirect():
    return redirect(url_for("home"))
@app.route("/")
def home():
    # Get number of items in the cart for display in navbar and add "cart" sessoin if not present
    if type(session.get("cart")) == NoneType:
        session["cart"] = js_dumps({})
        session.permanent = True
        cart = 0
    else:
        cart = ast.literal_eval(session["cart"])
        items_in_cart = 0
        for key in cart:
            items_in_cart = items_in_cart + cart[key]
        cart = items_in_cart
    # ---

    session["account"] = "lul"
    session.pop("account")
    return render_template("home.html", deals = deals, root = root, cart = cart)

# --- PRODUCTS ---
@app.route("/products")
def products():
    
    # Get number of items in the cart for display in navbar and add "cart" sessoin if not present
    if type(session.get("cart")) == NoneType:
        session["cart"] = js_dumps({})
        session.permanent = True
        cart = 0
    else:
        cart = ast.literal_eval(session["cart"])
        items_in_cart = 0
        for key in cart:
            items_in_cart = items_in_cart + cart[key]
        cart = items_in_cart
    # ---
    
    # Get products from database
    items = Item.query.limit(36).all()
    
    return render_template("products.html", items = items, root = root, cart = cart)

# --- CART ---
@app.route("/cart")
def cart():
    
    # Make an list of all items in the users cart # TODO:FIX FOR DICT
    cart = ast.literal_eval(session["cart"])
    items = []
    total = 0
    for key in cart:
        item = Item.query.filter_by(id=key).first()
        items.append([item, cart[key]])
        total = total + int(item.price) * cart[key]
    # ---
    
    # Get number of items in the cart for display in navbar and add "cart" sessoin if not present
    if type(session.get("cart")) == NoneType:
        session["cart"] = js_dumps({})
        session.permanent = True
        cart = 0
    else:
        cart = ast.literal_eval(session["cart"])
        items_in_cart = 0
        for key in cart:
            items_in_cart = items_in_cart + cart[key]
        cart = items_in_cart
    # ---
        
    return render_template("cart.html", items = items, cart = cart, total = str(total))

# --- ADD TO CART --- # Gets triggered automatically when the user presses "add to cart"
@app.route("/add_to_cart", methods = ["POST"])
def add_to_cart():
    item_id  = request.form.get('item_id')
    
    cart = ast.literal_eval(session["cart"])
    #cart.append(str(item_id))
    if item_id in cart:
        cart[item_id] = cart[item_id] + 1
    else:
        cart[item_id] = 1
    
    resp = make_response(render_template_string("success"))
    session["cart"] = js_dumps(cart)
    
    return resp

# --- REMOVE FROM CART --- # Gets triggered automatically when the user presses the trashcan in the cart page
@app.route("/remove_from_cart", methods = ["POST"])
def remove_from_cart():
    item_id  = request.form.get('item_id')
    
    cart = ast.literal_eval(session["cart"])
    #cart.remove(str(item_id))
    
    if item_id in cart:
        cart[item_id] = cart[item_id] - 1
        if cart[item_id] == 0:
            cart.pop(item_id)
    
    resp = make_response(render_template_string("success"))
    session["cart"] = js_dumps(cart)
    
    return resp

# --- CLEAR CART --- # Gets triggered automatically when the user presses "Clear Cart"
@app.route("/clear_cart", methods = ["POST"])
def clear_cart():
    resp = make_response(redirect(url_for("cart")))
    session["cart"] = js_dumps({})
    return resp

# --- REGISTER ---
@app.route("/register", methods = ["POST", "GET"])
def register():
    # Get number of items in the cart for display in navbar and add "cart" sessoin if not present
    if type(session.get("cart")) == NoneType:
        session["cart"] = js_dumps({})
        session.permanent = True
        cart = 0
    else:
        cart = ast.literal_eval(session["cart"])
        items_in_cart = 0
        for key in cart:
            items_in_cart = items_in_cart + cart[key]
        cart = items_in_cart
    # ---
    if request.method == "GET":
        
        resp = make_response(render_template("register.html", cart = cart, root = root, msg = [["",""],["",""],["",""],["",""],["",""]]))
        return resp
    else:
        email  = request.form.get('inputmail')
        uname  = request.form.get('inputuname')
        firstname  = request.form.get('inputname')
        lastname  = request.form.get('inputlastname')
        pwd  = request.form.get('inputpassword')
        pwd2  = request.form.get('inputpasswordconfirmation')
        
        msg = []
        error = False
        # Will be cleaned up later
        if not re.match(r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])""", email):
            error = True
            msg.append(["error", email, "Please provide a valid email adress"])
        else:
            msg.append(["success", email, ""])
        if not len(uname) >= 3:
            error = True
            msg.append(["error", uname, "Username must be at least 3 characters"])
        else:
            msg.append(["success", uname, ""])
        if not len(firstname) > 0:
            error = True
            msg.append(["error", firstname, "Please provide an name"])
        else:
            msg.append(["success", firstname, ""])
        if not len(lastname) > 0:
            error = True
            msg.append(["error", lastname], "Please provide an name")
        else:
            msg.append(["success", lastname, ""])
            
        if not len(pwd) > 8 or not len(pwd) <= 99 or not pwd == pwd2:
            error = True
            msg.append(["error", "", "Password must be at least 8 characters (max.99)<br>Passwords do not match"])
        else:
            msg.append(["success", pwd])
            
        if error:
            resp = make_response(render_template("register.html", cart = cart, root = root, msg = msg))
            return resp
        db.session.add(
            User(
                username=uname,
                firstname = firstname,
                lastname = lastname,
                email = email,
                password_hash = bcrypt.generate_password_hash(pwd)
            )
        )
        db.session.commit()
        return redirect(url_for("login"))

# --- LOG IN ---
@app.route("/login", methods = ["GET"])
def login():
    # Get number of items in the cart for display in navbar and add "cart" sessoin if not present
    if type(session.get("cart")) == NoneType:
        session["cart"] = js_dumps({})
        session.permanent = True
        cart = 0
    else:
        cart = ast.literal_eval(session["cart"])
        items_in_cart = 0
        for key in cart:
            items_in_cart = items_in_cart + cart[key]
        cart = items_in_cart
    # ---

# --- NEWSLETTER ---
#TODO: better newsletter stuff
@app.route('/newsletter/apply', methods = ["POST", "GET"])
def noo():
   if request.method == 'POST':
      email = request.form['email']
      return redirect(url_for('verify', id = email))
   else:
      return redirect(url_for('home'))

@app.route('/newsletter/verify/<id>')
def verify(id="none"):
    if id != "none":
        return f"Please verify your email '{id}'"
    else:
        return redirect(url_for('home'))

if __name__ == "__main__":
    #db.create_all()
    app.run(port=80, debug=True)