from types import NoneType
from flask import Flask, render_template, request, redirect, url_for, make_response, render_template_string, session
from flask_sqlalchemy import SQLAlchemy
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
    
class Account(db.Model):
    username = db.Column(db.String(24), unique=True, nullable=False, primary_key=True)
    firstname = db.Column(db.String(40), unique=False, nullable=False)
    lastname = db.Column(db.String(40), unique=False, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    billing_adress = db.Column(db.String(80), unique=True, nullable=False)
    shipping_adress = db.Column(db.String(80), unique=True, nullable=False)
    balance = db.Column(db.String(24), unique=False, nullable=False)
    blocked = db.Column(db.String(1), unique=False, nullable=False)
    password_hash = db.Column(db.String(60), unique=False, nullable=False)


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
        session["cart"] = js_dumps([])
        cart = 0
    else:
        cart = len(ast.literal_eval(session["cart"]))
    # ---

    session["account"] = "lul"
    session.pop("account")
    return render_template("home.html", deals = deals, root = root, cart = cart)

# --- PRODUCTS ---
@app.route("/products")
def products():
    
    # Get number of items in the cart for display in navbar and add "cart" sessoin if not present
    if type(session.get("cart")) == NoneType:
        session["cart"] = js_dumps([])
        cart = 0
    else:
        cart = len(ast.literal_eval(session["cart"]))
    # ---
    
    # Get products from database
    items = Item.query.limit(36).all()
    
    return render_template("products.html", items = items, root = root, cart = cart)

# --- CART ---
@app.route("/cart")
def cart():
    
    # Make an list of all items in the users cart
    cart = ast.literal_eval(session["cart"])
    items = []
    total = 0
    for id_ in cart:
        item = Item.query.filter_by(id=id_).first()
        items.append(item)
        total = total + int(item.price)
    # ---
    
    # Get number of items in the cart for display in navbar and add "cart" sessoin if not present
    if type(session.get("cart")) == NoneType:
        session["cart"] = js_dumps([])
        cart = 0
    else:
        cart = len(ast.literal_eval(session["cart"]))
    # ---
        
    return render_template("cart.html", items = items, cart = cart, total = str(total))

# --- ADD TO CART --- # Gets triggered automatically when the user presses "add to cart"
@app.route("/add_to_cart", methods = ["POST"])
def add_to_cart():
    item_id  = request.form.get('item_id')
    
    cart = ast.literal_eval(session["cart"])
    cart.append(str(item_id))
    
    resp = make_response(render_template_string("success"))
    session["cart"] = js_dumps(cart)
    
    return resp

# --- REMOVE FROM CART --- # Gets triggered automatically when the user presses the trashcan in the cart page
@app.route("/remove_from_cart", methods = ["POST"])
def remove_from_cart():
    item_id  = request.form.get('item_id')
    
    cart = ast.literal_eval(session["cart"])
    cart.remove(str(item_id))
    
    resp = make_response(render_template_string("success"))
    session["cart"] = js_dumps(cart)
    
    return resp

# --- CLEAR CART --- # Gets triggered automatically when the user presses "Clear Cart"
@app.route("/clear_cart", methods = ["POST"])
def clear_cart():
    resp = make_response(redirect(url_for("cart")))
    session["cart"] = js_dumps([])
    return resp

# --- SIGNUP ---
@app.route("/signup", methods = ["POST", "GET"])
def sign_up():
    if request.method == "GET":
        # Get number of items in the cart for display in navbar and add "cart" sessoin if not present
        if type(session.get("cart")) == NoneType:
            session["cart"] = js_dumps([])
            cart = 0
        else:
            cart = len(ast.literal_eval(session["cart"]))
        # ---
        
        resp = make_response(render_template("signup.html", cart = cart, root = root))
        return resp
    else:
        mail  = request.form.get('inputmail')
        uname  = request.form.get('inputuname')
        firstname  = request.form.get('inputname')
        lastname  = request.form.get('inputlastname')
        pwd  = request.form.get('inputpassword')
        pwd2  = request.form.get('inputpasswordconfirmation')
        """
        if not re.match(r"^([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])\x22)(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x22([^\x0d\x22\x5c\x80-\xff]|\x5c[\x00-\x7f])\x22))\x40([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])\x5d)(\x2e([^\x00-\x20\x22\x28\x29\x2c\x2e\x3a-\x3c\x3e\x40\x5b-\x5d\x7f-\xff]+|\x5b([^\x0d\x5b-\x5d\x80-\xff]|\x5c[\x00-\x7f])\x5d))(.\w{2,})+$", email):
            return "invalid mail"
        if not len(uname) >= 3:
            return "invalid uname"
        if not len(firstname) > 0:
            return "invalid name"
        if not len(lastname) > 0:
            return "invalid lastname"
        if not len(pwd) > 8:
            return "pwd to short"
        if not len(pwd) <= 99:
            return "pwd to long"
        if not pwd == pwd2:
            return "pwd != pwd2"""
        
        return str(Item.query.filter_by(price=uname).all())

# --- NEWSLETTER ---
#TODO: better newsletter stuff
@app.route('/newsletter/apply', methods = ["POST", "GET"])
def login():
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