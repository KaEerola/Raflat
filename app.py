import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, flash, abort, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import db
import config
import restaurants

app = Flask(__name__)
app.secret_key = config.SECRET_KEY 

def require_login():
    if "user_id" not in session:
        abort(403)

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
        flash("Tunnus luotu", "")
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return redirect("/")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        sql = "SELECT id, password_hash FROM users WHERE username = ?"
        result = db.query(sql, [username])
        
        if result:
            user_id, password_hash = result[0]
            if check_password_hash(password_hash, password):
                session["username"] = username
                session["user_id"] = user_id
                return redirect("/")
        
        return "VIRHE: väärä tunnus tai salasana"


@app.route("/logout")
def logout():
    del session["username"]
    del session["user_id"]
    return redirect("/")

@app.route("/new_restaurant", methods=["GET", "POST"])
def new_restaurants():
    require_login()

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
    reviews = restaurants.get_reviews(restaurant_id)
    return render_template("restaurant.html", restaurant=restaurant, reviews=reviews)

@app.route("/edit_restaurant/<int:restaurant_id>")
def edit_restaurant(restaurant_id):
    restaurant = restaurants.get_restaurant(restaurant_id)
    return render_template("edit_restaurant.html", restaurant = restaurant)

@app.route("/update_restaurant", methods=["POST"])
def update_restaurant():
    restaurant_id = request.form["id"]
    name = request.form["name"]
    address = request.form["address"]
    link = request.form["link"]
    
    restaurants.update_restaurant(restaurant_id, name, address, link)

    flash('Ravintola päivitetty', "")

    return redirect("/restaurants")
        
    
@app.route("/remove_restaurant/<int:restaurant_id>", methods=["GET", "POST"])
def remove_restaurant(restaurant_id):
    restaurant = restaurants.get_restaurant(restaurant_id)
    if request.method == "GET":
        return render_template("remove_restaurant.html", restaurant = restaurant)
    if request.method == "POST":
        restaurants.remove_restaurant(restaurant["id"])
        return redirect("/restaurants")

@app.route("/search")
def search():
    query = request.args.get("query")
    if query:
        results = restaurants.find_restaurant(query)
    else:
        query = ""
        results = []
    return render_template("search.html", query=query, results=results)
    
@app.route("/add_review/<int:restaurant_id>", methods=["GET", "POST"])
def add_review(restaurant_id):
    if request.method == "GET":
        restaurant = restaurants.get_restaurant(restaurant_id)
        return render_template("add_review.html", restaurant = restaurant)
    if request.method == "POST":
        comment = request.form["comment"]
        user_id = session["user_id"]
        rating = request.form["rating"]
        restaurants.add_review(restaurant_id, user_id, rating, comment)
        flash('Arvostelu lisätty', "")
        return redirect("/restaurants")

@app.route("/remove_review/<int:review_id>", methods=["GET", "POST"])
def remove_review(review_id):
    if request.method == "GET":
        review = restaurants.get_review(review_id)
        restaurant = restaurants.get_restaurant(review["restaurant_id"])
        return render_template("remove_review.html", review=review, restaurant=restaurant)
    
    if request.method == "POST":
        review = restaurants.get_review(review_id)
        restaurant_id = review["restaurant_id"]
        restaurants.remove_review(review_id)
        flash('Arvostelu poistettu', "")
        return redirect(url_for("show_restaurant", restaurant_id=restaurant_id))
