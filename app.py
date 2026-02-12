import os
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ---------------- DATABASE ----------------

user_interests = db.Table('user_interests',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('interest_id', db.Integer, db.ForeignKey('interest.id'))
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    college = db.Column(db.String(100))
    bio = db.Column(db.String(300))
    contact_info = db.Column(db.String(100))
    profile_pic = db.Column(db.String(200))

    interests = db.relationship('Interest', secondary=user_interests, backref='users')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Interest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def seed_interests():
    default_interests = [
        "Football",
        "Hackathons",
        "Web Development",
        "Machine Learning",
        "Research",
        "Startups",
        "Gaming",
        "Gym/Fitness"
    ]

    for name in default_interests:
        if not Interest.query.filter_by(name=name).first():
            db.session.add(Interest(name=name))

    db.session.commit()


# ---------------- ROUTES ----------------

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    interests = Interest.query.all()

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        college = request.form.get("college")
        bio = request.form.get("bio")
        contact_info = request.form.get("contact")
        selected_interest_ids = request.form.getlist("interests")

        if User.query.filter_by(email=email).first():
            return "Email already exists"

        file = request.files.get("profile_pic")
        filename = None

        if file and file.filename != "":
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_user = User(
            name=name,
            email=email,
            college=college,
            bio=bio,
            contact_info=contact_info,
            profile_pic=filename
        )

        new_user.set_password(password)

        for interest_id in selected_interest_ids:
            interest = Interest.query.get(int(interest_id))
            if interest:
                new_user.interests.append(interest)

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html", interests=interests)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))
        else:
            return "Invalid credentials"

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    user_interest_ids = [i.id for i in current_user.interests]

    same_college_users = User.query.filter(
        User.college == current_user.college,
        User.id != current_user.id
    ).all()

    matched_users = []

    for user in same_college_users:
        other_ids = [i.id for i in user.interests]
        shared_ids = set(user_interest_ids) & set(other_ids)

        if shared_ids:
            shared_interests = Interest.query.filter(Interest.id.in_(shared_ids)).all()

            percentage = int((len(shared_ids) / len(user_interest_ids)) * 100) if user_interest_ids else 0

            matched_users.append({
                "user": user,
                "shared_interests": shared_interests,
                "percentage": percentage
            })

    matched_users.sort(key=lambda x: x["percentage"], reverse=True)

    return render_template(
        "dashboard.html",
        matches=matched_users,
        match_count=len(matched_users)
    )


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("landing"))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_interests()
    app.run(debug=True)
