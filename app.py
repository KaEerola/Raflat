import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, flash, abort, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import db
import config
import restaurants
import users

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
        all_tags = restaurants.get_tags()  

        return render_template("new_restaurant.html", tags=all_tags,)

    if request.method == "POST":
        name = request.form["name"]
        address = request.form["address"]
        link = request.form["link"]
        user_id = session["user_id"]

        restaurants.add_restaurant(name, address, link, user_id)

        restaurant_id = restaurants.find_restaurant(name)[0][0]
        tags = request.form.getlist("tags")
        if tags:
            for tag in tags:
                restaurants.associate_tag_with_restaurant(restaurant_id, tag)
        
        flash("Ravintola lisätty", "")
        return redirect("/restaurants")

@app.route("/create_tag", methods=["POST"])
def create_tag_route():
    require_login()
    user_id = session["user_id"]
    new_tag_name = request.form["new_tag_name"].strip().lower()
    
    if not new_tag_name:
        flash("Tagi ei voi olla tyhjä", "error")
    else:
        restaurants.create_tag(user_id, new_tag_name)
        flash(f"Tagi '{new_tag_name}' lisätty", "success")

    return redirect(request.referrer or "/")
    
@app.route("/restaurants")
def show_restaurants():
    rest = restaurants.get_restaurants()
    return render_template("restaurants.html", restaurants=rest)

@app.route("/restaurant/<int:restaurant_id>")
def show_restaurant(restaurant_id):
    restaurant = restaurants.get_restaurant(restaurant_id)
    tags = restaurants.get_tags()
    restaurant_tags = restaurants.get_restaurant_tags(restaurant_id)
    reviews = restaurants.get_reviews(restaurant_id)
    return render_template("restaurant.html", restaurant=restaurant, reviews=reviews, tags=tags, restaurant_tags=restaurant_tags)

@app.route("/remove_tag_from_restaurant", methods=["POST"])
def remove_tag_from_restaurant():
    restaurant_id = request.form["restaurant_id"]
    tag_id = request.form["tag_id"]

    restaurants.remove_tag_from_restaurant(restaurant_id, tag_id)

    # Redirect back to the restaurant detail page
    return redirect(request.referrer or "/restaurants")


@app.route("/add_tags/<int:restaurant_id>", methods=["POST"])
def add_tags(restaurant_id):
    tags = request.form.getlist("tags")
    if tags:
        for tag in tags:
            restaurants.associate_tag_with_restaurant(restaurant_id, tag)
    flash('Tagit lisätty', "")
    return redirect(url_for("show_restaurant", restaurant_id=restaurant_id))

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

@app.route("/search_restaurants")
def search():
    query = request.args.get("query")
    
    if query and len(query) < 3:
        flash('Hakusana liian lyhyt', "error")
        return redirect("/search_restaurants")
    
    if query and len(query) >= 3:
        results = restaurants.find_restaurant(query)
        return render_template("search_restaurants.html", query=query, results=results)
    
    # If no query at all (e.g., first time loading the page)
    results = []
    return render_template("search_restaurants.html", query="", results=results)

    
    
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
    
@app.route("/edit_review/<int:review_id>")
def edit_review(review_id):
    review = restaurants.get_review(review_id)
    restaurant = restaurants.get_restaurant(review["restaurant_id"])
    return render_template("edit_review.html", review=review, restaurant=restaurant)

@app.route("/update_review", methods = ["POST"])
def update_review():
    review_id= request.form["id"]
    rating = request.form["rating"]
    comment = request.form["comment"]
    restaurant_id = request.form["restaurant_id"]

    restaurants.update_review(review_id, rating, comment)

    flash('Arvostelu muokattu', "")
    return redirect(url_for('show_restaurant', restaurant_id=restaurant_id))

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
    
@app.route("/user/<string:username>")
def show_user(username):
    user = users.get_user(username)  
    
    if not user:
        return "VIRHE: käyttäjää ei löydy"
    
    user_id = user[0]
    
    restaurants = users.get_user_restaurants(user_id)  
    reviews = users.get_user_reviews(user_id)  
    tags = users.get_user_tags(user_id)
    
    return render_template("user.html", user=user, reviews=reviews, restaurants=restaurants, tags=tags)
