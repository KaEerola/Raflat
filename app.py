import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import db
import config
import restaurants

app = Flask(__name__)
app.secret_key = config.SECRET_KEY 

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    password_hash = generate_password_hash(password1, method='pbkdf2:sha256')

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return "Tunnus luotu"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        sql = "SELECT password_hash FROM users WHERE username = ?"
        password_hash = db.query(sql, [username])[0][0]

        if check_password_hash(password_hash, password):
            session["username"] = username
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/new_restaurant", methods=["GET", "POST"])
def new_restaurants():
    if request.method == "GET":
        return render_template("new_restaurant.html")
    
    if request.method == "POST":
        name = request.form["name"]
        address = request.form["address"]
        link = request.form["link"]
        restaurants.add_restaurant(name, address, link)

        flash('Ravintola lisätty', "")

        return redirect("/")
    
@app.route("/restaurants")
def show_restaurants():
    rest = restaurants.get_restaurants()
    print(rest)
    return render_template("restaurants.html", restaurants=rest)

@app.route("/restaurant/<int:restaurant_id>")
def show_restaurant(restaurant_id):
    restaurant = restaurants.get_restaurant(restaurant_id)
    return render_template("restaurant.html", restaurant=restaurant)

@app.route("/edit/<int:restaurant_id>", methods=["GET", "POST"])
def edit_restaurant(restaurant_id):
    restaurant = restaurants.get_restaurant(restaurant_id)
    
    if request.method == "GET":
        return render_template("edit.html", restaurant = restaurant)

    if request.method == "POST":
        name = request.form.get("name") or restaurant["name"]
        address = request.form.get("address") or restaurant["address"]
        link = request.form.get("link") or restaurant["link"]
        restaurants.update_restaurant(restaurant_id, name, address, link)
        return redirect("/restaurants")
    
@app.route("/remove/<int:restaurant_id>", methods=["GET", "POST"])
def remove_restaurant(restaurant_id):
    restaurant = restaurants.get_restaurant(restaurant_id)
    if request.method == "GET":
        return render_template("remove.html", restaurant = restaurant)
    if request.method == "POST":
        restaurants.remove_restaurant(restaurant["id"])
        return redirect("/restaurants")