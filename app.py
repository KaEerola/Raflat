import sqlite3
import secrets
import markupsafe
from flask import Flask
from flask import redirect, render_template, request, session, flash, abort, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import db
import config
import restaurants
import users
import tags

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

def require_login():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    form_token = request.form.get("csrf_token")
    session_token = session.get("csrf_token")
    if not form_token or not session_token or form_token != session_token:
        abort(403)

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register", methods = ["POST"])
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

    return redirect("/login"), flash("Rekisteröityminen onnistui", "success")


@app.route("/login", methods = ["GET", "POST"])
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
                session["csrf_token"] = secrets.token_hex(16)
                session["username"] = username
                session["user_id"] = user_id
                return redirect("/"), flash("Kirjautuminen onnistui", "success")
        return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    del session["username"]
    del session["user_id"]
    del session["csrf_token"]
    return redirect("/"), flash("Uloskirjautuminen onnistui", "success")

@app.route("/new_restaurant", methods = ["GET", "POST"])
def new_restaurants():
    require_login()
    if request.method == "GET":
        all_tags = restaurants.get_tags()
        return render_template("new_restaurant.html", tags = all_tags,)
    if request.method == "POST":
        check_csrf()
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
        return redirect("/restaurants"), flash("Ravintola lisätty", "success")

@app.route("/create_tag", methods = ["POST"])
def create_tag_route():
    require_login()
    check_csrf()
    user_id = session["user_id"]
    new_tag_name = request.form["new_tag_name"].strip().lower()
    if not new_tag_name:
        message = flash("Tagi ei voi olla tyhjä", "error")
    else:
        tags.create_tag(user_id, new_tag_name)
        message = flash(f"Tagi '{new_tag_name}' lisätty", "success")
    return redirect(request.referrer or "/"), message

@app.route("/restaurants")
def show_restaurants():
    limit = request.args.get("limit", default = 5, type = int)
    page = request.args.get("page", default = 1, type = int)

    restaurant_list = restaurants.get_restaurants(page, limit)
    total = restaurants.get_restaurant_count()
    total_pages = (total + limit - 1) // limit  # ceiling division

    return render_template(
        "restaurants.html",
        restaurants = restaurant_list,
        current_limit = limit,
        current_page = page,
        total_pages = total_pages)

@app.route("/restaurant/<int:restaurant_id>")
def show_restaurant(restaurant_id):
    restaurant = restaurants.get_restaurant(restaurant_id)
    all_tags = tags.get_tags()
    restaurant_tags = tags.get_restaurant_tags(restaurant_id)
    average_rating = restaurants.get_average_rating(restaurant_id)
    sort = request.args.get("sort", default="newest")
    page = request.args.get("page", default=1, type=int)
    limit = 5
    offset = (page - 1) * limit
    reviews = restaurants.get_reviews(restaurant_id, sort=sort, limit=limit, offset=offset)
    total_reviews = restaurants.count_reviews(restaurant_id)
    total_pages = (total_reviews + limit - 1) // limit

    if average_rating is not None:
        average_rating = round(average_rating, 2)
    else:
        average_rating = "Ei arvosteluja"

    return render_template(
        "restaurant.html",
        restaurant = restaurant,
        tags = all_tags,
        restaurant_tags = restaurant_tags,
        average_rating = average_rating,
        reviews = reviews,
        sort = sort,
        current_page = page,
        total_pages = total_pages
    )

@app.route("/remove_tag_from_restaurant", methods = ["POST"])
def remove_tag_from_restaurant():
    check_csrf()
    require_login()
    restaurant_id = request.form["restaurant_id"]
    tag_id = request.form["tag_id"]
    tags.remove_tag_from_restaurant(restaurant_id, tag_id)
    # Redirect back to the restaurant detail page
    return redirect(request.referrer or "/restaurants")

@app.route("/add_tags/<int:restaurant_id>", methods = ["POST"])
def add_tags(restaurant_id):
    check_csrf()
    require_login()
    tags_adding = request.form.getlist("tags")
    if tags_adding:
        for tag in tags_adding:
            tags.associate_tag_with_restaurant(restaurant_id, tag)
    return redirect(url_for("show_restaurant",
                            restaurant_id = restaurant_id)), flash('Tagit lisätty', "success")

@app.route("/edit_restaurant/<int:restaurant_id>")
def edit_restaurant(restaurant_id):
    restaurant = restaurants.get_restaurant(restaurant_id)
    return render_template("edit_restaurant.html", restaurant = restaurant)

@app.route("/update_restaurant", methods = ["POST"])
def update_restaurant():
    check_csrf()
    restaurant_id = request.form["id"]
    name = request.form["name"]
    address = request.form["address"]
    link = request.form["link"]
    restaurants.update_restaurant(restaurant_id, name, address, link)
    return redirect("/restaurants"), flash('Ravintola päivitetty', "success")

@app.route("/remove_restaurant/<int:restaurant_id>", methods = ["GET", "POST"])
def remove_restaurant(restaurant_id):
    require_login()
    restaurant = restaurants.get_restaurant(restaurant_id)
    if request.method == "GET":
        return render_template("remove_restaurant.html", restaurant = restaurant)
    if request.method == "POST":
        check_csrf()
        restaurants.remove_restaurant(restaurant["id"])
        return redirect("/restaurants")

@app.route("/add_review/<int:restaurant_id>", methods = ["GET", "POST"])
def add_review(restaurant_id):
    require_login()
    if request.method == "GET":
        restaurant = restaurants.get_restaurant(restaurant_id)
        return render_template("add_review.html", restaurant = restaurant)
    if request.method == "POST":
        check_csrf()
        comment = request.form["comment"]
        user_id = session["user_id"]
        rating = request.form["rating"]
        restaurants.add_review(restaurant_id, user_id, rating, comment)
        return redirect(url_for('show_restaurant',
                            restaurant_id = restaurant_id)), flash('Arvostelu lisätty', "success")

@app.route("/edit_review/<int:review_id>")
def edit_review(review_id):
    require_login()
    review = restaurants.get_review(review_id)
    restaurant = restaurants.get_restaurant(review["restaurant_id"])
    return render_template("edit_review.html", review = review, restaurant = restaurant)

@app.route("/update_review", methods = ["POST"])
def update_review():
    require_login()
    check_csrf()
    review_id = request.form["id"]
    rating = request.form["rating"]
    comment = request.form["comment"]
    restaurant_id = request.form["restaurant_id"]
    restaurants.update_review(review_id, rating, comment)
    return redirect(url_for('show_restaurant',
                            restaurant_id = restaurant_id)), flash('Arvostelu muokattu', "success")

@app.route("/remove_review/<int:review_id>", methods = ["GET", "POST"])
def remove_review(review_id):
    require_login()
    if request.method == "GET":
        review = restaurants.get_review(review_id)
        restaurant = restaurants.get_restaurant(review["restaurant_id"])
        return render_template("remove_review.html", review = review, restaurant = restaurant)
    if request.method == "POST":
        check_csrf()
        review = restaurants.get_review(review_id)
        restaurant_id = review["restaurant_id"]
        restaurants.remove_review(review_id)
        return redirect(url_for("show_restaurant",
                                restaurant_id = restaurant_id)), flash('Arvostelu poistettu'
                                                                       , "success")

@app.route("/user/<string:username>/")
def show_user(username):
    user = users.get_user(username)
    if not user:
        return "VIRHE: käyttäjää ei löydy"
    user_id = user[0]
    restaurant_limit = request.args.get("restaurant_limit", default=5, type=int)
    restaurant_page = request.args.get("restaurant_page", default=1, type=int)
    added_restaurants = users.get_user_restaurants(user["id"], restaurant_page, restaurant_limit)
    total_restaurants = users.count_restaurants_by_user(user["id"])
    restaurant_total_pages = (total_restaurants + restaurant_limit - 1) // restaurant_limit
    review_limit = 5
    review_page = request.args.get("review_page", default=1, type=int)
    reviews = users.get_user_reviews(user["id"], review_page, review_limit)
    total_reviews = users.count_reviews_by_user(user["id"])
    review_total_pages = (total_reviews + restaurant_limit - 1) // restaurant_limit
    tags = users.get_user_tags(user_id)
    return render_template("user.html", user = user, reviews = reviews,
                           added_restaurants = added_restaurants, tags = tags,
                            restaurant_current_limit = restaurant_limit,
                            restaurant_current_page = restaurant_page,
                            restaurant_total_pages = restaurant_total_pages,
                            review_current_page = review_page,
                            review_total_pages = review_total_pages)

@app.route("/delete_tag", methods=["POST"])
def delete_tag():
    tag_id = request.form.get("tag_id")
    check_csrf()
    require_login()

    # Check user is the owner of the tag (security step)
    tag = tags.get_tag_by_id(tag_id)
    if tag["user_id"] != session.get("user_id"):
        abort(403)

    # Delete associations first, then the tag
    tags.remove_tag_associations(tag_id)
    tags.delete_tag(tag_id)

    flash("Tagi poistettu pysyvästi.", "success")
    return redirect(request.referrer or "/")

@app.route("/search_restaurants")
def search_restaurants():
    query = request.args.get("query", "")
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=5, type=int)
    if query and len(query) < 3:
        flash('Hakusana liian lyhyt', "error")
        return redirect("/search_restaurants")
    results = []
    total_pages = 0
    total_results = 0
    if query and len(query) >= 3:
        results = restaurants.find_restaurant(query, page, limit)
        total_results = restaurants.count_restaurant_matches(query)
        total_pages = (total_results + limit - 1) // limit
    return render_template(
        "search_restaurants.html",
        query = query,
        results = results,
        current_page = page,
        total_pages = total_pages,
        current_limit = limit)


@app.route("/search_users")
def search_users():
    query = request.args.get("query", "")
    page = request.args.get("page", default=1, type=int)
    limit = request.args.get("limit", default=5, type=int)
    total_pages = 0
    total_results = 0
    results = []
    if query and len(query) < 3:
        flash('Hakusana liian lyhyt', "error")
        return redirect("/search_users")
    if query and len(query) >= 3:
        results = users.find_users(query, page, limit)
        total_results = users.count_user_matches(query)
        total_pages = (total_results + limit - 1) // limit
    elif query:
        flash('Hakusana liian lyhyt', "error")
        return redirect("/search_users")
    return render_template("search_users.html", query = query,
                            results = results,
                            current_page = page,
                            total_pages = total_pages,
                            current_limit = limit)

