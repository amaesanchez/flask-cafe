"""Flask App for Flask Cafe."""

from flask import Flask, render_template, redirect, request, url_for, flash, session, g, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import os

from models import db, connect_db, Cafe, City, User, Like, DEFAULT_IMG_URL, DEFAULT_PROFILE_URL
from forms import CafeForm, SignupForm, LoginForm, ProfileForm, CSRFProtectionForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

toolbar = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

import seed

#######################################
# auth & auth routes

CURR_USER_KEY = "curr_user"
NOT_LOGGED_IN_MSG = "You are not logged in."
NOT_ADMIN_MSG = "You are not authorized to access this page."


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

@app.before_request
def generate_CSRF_form():
    """ instantiates CSRF form """

    g.csrf_form = CSRFProtectionForm()


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.errorhandler(404)
def not_found(err):
  return render_template('404.html'), 404

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """ Display registration form, or post new user """

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

    form = SignupForm()

    if form.validate_on_submit():
        try:
            user = User.register(
                username = form.username.data,
                email = form.email.data,
                first_name = form.first_name.data,
                last_name = form.last_name.data,
                description = form.description.data,
                password = form.password.data,
                image_url = form.image_url.data or None
            )

            db.session.commit()

            do_login(user)

            flash(f"You are signed up and logged in.", 'success')
            return redirect('/cafes')

        except IntegrityError:
            flash("Username already taken", 'danger')

    return render_template('/auth/signup-form.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """ Display login form, or logs user in """

    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)

            flash(f"Hello, {user.username}!", 'success')
            return redirect('/cafes')

        flash("Invalid credentials.", 'danger')

    return render_template('/auth/login-form.html', form=form)

@app.post('/logout')
def logout():
    """ Logs out user """

    if g.csrf_form.validate_on_submit() and g.user:
        do_logout()
        flash('You should have successfully logged out.', 'success')

    return redirect('/')


#######################################
# homepage

@app.get('/')
def homepage():
    """Show homepage."""

    return render_template("homepage.html")


#######################################
# cafes


@app.get('/cafes')
def cafe_list():
    """Return list of all cafes."""

    cafes = Cafe.query.order_by('name').all()

    return render_template(
        'cafe/list.html',
        cafes=cafes,
    )

@app.get('/cafes/<int:cafe_id>')
def cafe_detail(cafe_id):
    """Show detail for cafe."""

    cafe = Cafe.query.get_or_404(cafe_id)

    map = cafe.save_map()

    return render_template('/cafe/detail.html',
        cafe=cafe, map=map)

@app.route('/cafes/add', methods=['GET', 'POST'])
def add_cafe():
    """ Display add cafe form, or post a new cafe """

    if not g.user:
        flash(NOT_LOGGED_IN_MSG, 'danger')
        return redirect('/')

    if not g.user.admin:
        flash(NOT_ADMIN_MSG, 'danger')
        return redirect('/cafes')

    form = CafeForm()
    form.city_code.choices = City.get_choices()

    if form.validate_on_submit():
        cafe = Cafe(
            name=form.name.data,
            description=form.description.data,
            url=form.url.data,
            address=form.address.data,
            city_code=form.city_code.data,
            image_url=form.image_url.data or None
        )

        db.session.add(cafe)
        db.session.commit()

        flash(f'{cafe.name} added!', 'success')
        redirect_url=url_for('cafe_detail', cafe_id=cafe.id)
        return redirect(redirect_url)

    return render_template('/cafe/add-form.html', form=form)

@app.route('/cafes/<int:cafe_id>/edit', methods=['GET', 'POST'])
def edit_cafe(cafe_id):
    """ Display edit cafe form, or update cafe """

    if not g.user:
        flash(NOT_LOGGED_IN_MSG, 'danger')
        return redirect('/')

    if not g.user.admin:
        flash(NOT_ADMIN_MSG, 'danger')
        return redirect('/cafes')

    cafe = Cafe.query.get_or_404(cafe_id)

    form = CafeForm(obj=cafe)
    form.city_code.choices = City.get_choices()

    if form.validate_on_submit():
        form.populate_obj(cafe)
        cafe.image_url = form.image_url.data or DEFAULT_IMG_URL

        db.session.commit()

        flash(f'{cafe.name} edited!', 'success')
        redirect_url = url_for('cafe_detail', cafe_id=cafe.id)
        return redirect(redirect_url)

    return render_template('/cafe/edit-form.html', cafe=cafe, form=form)

#######################################
# users

@app.get('/profile')
def user_profile():
    """ Display user profile """

    if not g.user:
        flash(NOT_LOGGED_IN_MSG, 'danger')
        return redirect('/')

    return render_template('/profile/detail.html')

@app.route('/profile/edit', methods=['GET', 'POST'])
def edit_user():
    """ Display edit profile form or update profile """

    if not g.user:
        flash(NOT_LOGGED_IN_MSG, 'danger')
        return redirect('/')

    form = ProfileForm(obj=g.user)

    if form.validate_on_submit():
        form.populate_obj(g.user)
        g.user.image_url = form.image_url.data or DEFAULT_PROFILE_URL

        db.session.commit()

        flash('Profile edited!', 'success')
        redirect_url = url_for('user_profile')
        return redirect(redirect_url)

    return render_template('/profile/edit-form.html', form=form)


#######################################
# Likes API

@app.route('/api/likes', methods=['GET','POST'])
def like_cafe():
    """ Returns JSON of cafe's like status or
    updates user's likes list and returns JSON """
    if not g.user:
        return {"error": "Not logged in"}

    if request.method == 'GET':
        cafe_id = request.args.get('cafe_id')

        cafe = Cafe.query.get_or_404(cafe_id)

        status = cafe in g.user.liked_cafes
        return jsonify(likes=status)

    cafe_id = request.get_json()['cafe_id']

    cafe = Cafe.query.get_or_404(cafe_id)
    g.user.liked_cafes.append(cafe)

    db.session.commit()
    return (jsonify(liked=cafe_id), 201)



@app.post('/api/unlike')
def unlike_cafe():
    """ Removes cafe from user's likes list and returns JSON"""

    if not g.user:
        return {"error": "Not logged in"}

    cafe_id = request.get_json()['cafe_id']
    like = Like.query.get_or_404((g.user.id, cafe_id))

    db.session.delete(like)
    db.session.commit()

    return (jsonify(unliked=cafe_id), 201)


# when
