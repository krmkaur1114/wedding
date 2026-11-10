from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

app = Flask(__name__)

# Change the website name here only - it updates on every page
SITE_NAME = "Dream Wedding Events"

@app.context_processor
def inject_site_name():
    return {"site_name": SITE_NAME}

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# secret key from config.json (falls back to a dev key if file is missing)
if os.path.exists('config.json'):
    with open('config.json', 'r') as file:
        app.secret_key = json.load(file)["my_secret_key"]
else:
    app.secret_key = "change-this-secret-key"


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=False)
    phone = db.Column(db.String(20), nullable=True)
    date = db.Column(db.String(50), nullable=True)
    package = db.Column(db.String(100), nullable=True)
    message = db.Column(db.String(500), nullable=True)

    def __repr__(self):
        return f'<Booking {self.name}>'


class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(150), nullable=True)
    message = db.Column(db.String(1000), nullable=True)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    password = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/services")
def services():
    return render_template("services.html")


@app.route("/gallery")
def gallery():
    return render_template("gallery.html")


@app.route("/packages")
def packages():
    return render_template("packages.html")


@app.route("/rooms")
def rooms():
    return render_template("room.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        db.session.add(Contact(
            name=request.form.get("name"),
            email=request.form.get("email"),
            subject=request.form.get("subject"),
            message=request.form.get("message"),
        ))
        db.session.commit()
        flash("Thank you! Your message has been sent.", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html")


@app.route("/booking", methods=["GET", "POST"])
def booking():
    if request.method == "POST":
        name = request.form.get("name")
        db.session.add(Booking(
            name=name,
            email=request.form.get("email"),
            phone=request.form.get("phone"),
            date=request.form.get("date"),
            package=request.form.get("package"),
            message=request.form.get("message"),
        ))
        db.session.commit()
        return render_template("success.html", n=name)

    return render_template("booking.html", selected=request.args.get("package"))


@app.route("/success")
def success():
    return render_template("success.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")

        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template("register.html")

        if User.query.filter_by(email=email).first():
            flash("This email is already registered. Please login.", "error")
            return redirect(url_for("login"))

        db.session.add(User(name=name, email=email, phone=phone,
                            password=generate_password_hash(password)))
        db.session.commit()
        flash("Account created! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user'] = user.name
            session['email'] = user.email
            return redirect(url_for('dashboard'))

        flash("Wrong email or password. Please try again.", "error")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if 'user' not in session:
        return redirect(url_for("login"))

    my_bookings = Booking.query.filter_by(email=session['email']).all()
    return render_template("dashboard.html", name=session['user'], bookings=my_bookings)


@app.route("/logout")
def logout():
    session.clear()
    return render_template("logout.html")


if __name__ == "__main__":
    app.run(debug=True)
