"""Tests for Flask Cafe."""


import re
from unittest import TestCase

from flask import session
from app import app, CURR_USER_KEY
from models import db, Cafe, City, connect_db, User, Like

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql:///flaskcafe_test"
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Don't req CSRF for testing
app.config['WTF_CSRF_ENABLED'] = False

connect_db(app)

db.drop_all()
db.create_all()


#######################################
# helper functions for tests


def debug_html(response, label="DEBUGGING"):  # pragma: no cover
    """Prints HTML response; useful for debugging tests."""

    print("\n\n\n", "*********", label, "\n")
    print(response.data.decode('utf8'))
    print("\n\n")


def login_for_test(client, user_id):
    """Log in this user."""

    with client.session_transaction() as sess:
        sess[CURR_USER_KEY] = user_id


#######################################
# data to use for test objects / testing forms


CITY_DATA = dict(
    code="sf",
    name="San Francisco",
    state="CA"
)

CAFE_DATA = dict(
    name="Test Cafe",
    description="Test description",
    url="http://testcafe.com/",
    address="500 Sansome St",
    city_code="sf",
    image_url="http://testcafeimg.com/"
)

CAFE_DATA_EDIT = dict(
    name="new-name",
    description="new-description",
    url="http://new-image.com/",
    address="500 Sansome St",
    city_code="sf",
    image_url="http://new-image.com/"
)

TEST_USER_DATA = dict(
    username="test",
    first_name="Testy",
    last_name="MacTest",
    description="Test Description.",
    email="test@test.com",
    password="secret",
)

TEST_USER_DATA_EDIT = dict(
    first_name="new-fn",
    last_name="new-ln",
    description="new-description",
    email="new-email@test.com",
    image_url="http://new-image.com",
)

TEST_USER_DATA_NEW = dict(
    username="new-username",
    first_name="new-fn",
    last_name="new-ln",
    description="new-description",
    password="secret",
    email="new-email@test.com",
    image_url="http://new-image.com",
)

ADMIN_USER_DATA = dict(
    username="admin",
    first_name="Addie",
    last_name="MacAdmin",
    description="Admin Description.",
    email="admin@test.com",
    password="secret",
    admin=True,
)


#######################################
# homepage


class HomepageViewsTestCase(TestCase):
    """Tests about homepage."""

    def test_homepage(self):
        with app.test_client() as client:
            resp = client.get("/")
            self.assertIn(b'Where Coffee Dreams Come True', resp.data)


#######################################
# cities


class CityModelTestCase(TestCase):
    """Tests for City Model."""

    def setUp(self):
        """Before all tests, add sample city & users"""

        Cafe.query.delete()
        City.query.delete()

        sf = City(**CITY_DATA)
        db.session.add(sf)

        cafe = Cafe(**CAFE_DATA)
        db.session.add(cafe)

        db.session.commit()

        self.cafe = cafe

    def tearDown(self):
        """After each test, remove all cafes."""

        Cafe.query.delete()
        City.query.delete()
        db.session.commit()

    # depending on how you solve exercise, you may have things to test on
    # the City model, so here's a good place to put that stuff.


#######################################
# cafes


class CafeModelTestCase(TestCase):
    """Tests for Cafe Model."""

    def setUp(self):
        """Before all tests, add sample city & users"""

        Cafe.query.delete()
        City.query.delete()

        sf = City(**CITY_DATA)
        db.session.add(sf)

        cafe = Cafe(**CAFE_DATA)
        db.session.add(cafe)

        db.session.commit()

        self.cafe = cafe

    def tearDown(self):
        """After each test, remove all cafes."""

        Cafe.query.delete()
        City.query.delete()
        db.session.commit()

    def test_get_city_state(self):
        self.assertEqual(self.cafe.get_city_state(), "San Francisco, CA")


class CafeViewsTestCase(TestCase):
    """Tests for views on cafes."""

    def setUp(self):
        """Before all tests, add sample city & users"""

        Cafe.query.delete()
        City.query.delete()

        sf = City(**CITY_DATA)
        db.session.add(sf)

        cafe = Cafe(**CAFE_DATA)
        db.session.add(cafe)

        db.session.commit()

        self.cafe_id = cafe.id

    def tearDown(self):
        """After each test, remove all cafes."""

        Cafe.query.delete()
        City.query.delete()
        db.session.commit()

    def test_list(self):
        with app.test_client() as client:
            resp = client.get("/cafes")
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Test Cafe", resp.data)

    def test_detail(self):
        with app.test_client() as client:
            resp = client.get(f"/cafes/{self.cafe_id}")
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b"Test Cafe", resp.data)
            self.assertIn(b'testcafe.com', resp.data)


class CafeAdminViewsTestCase(TestCase):
    """Tests for add/edit views on cafes."""

    def setUp(self):
        """Before each test, add sample city, users, and cafes"""

        City.query.delete()
        Cafe.query.delete()

        sf = City(**CITY_DATA)
        db.session.add(sf)

        cafe = Cafe(**CAFE_DATA)
        db.session.add(cafe)

        db.session.commit()

        self.cafe_id = cafe.id

    def tearDown(self):
        """After each test, delete the cities."""

        Cafe.query.delete()
        City.query.delete()
        db.session.commit()

    def test_add(self):
        with app.test_client() as client:
            resp = client.get(f"/cafes/add")
            self.assertIn(b'Add Cafe', resp.data)

            resp = client.post(
                f"/cafes/add",
                data=CAFE_DATA_EDIT,
                follow_redirects=True)
            self.assertIn(b'added', resp.data)

    def test_dynamic_cities_vocab(self):
        id = self.cafe_id

        # the following is a regular expression for the HTML for the drop-down
        # menu pattern we want to check for
        choices_pattern = re.compile(
            r'<select [^>]*name="city_code"[^>]*><option [^>]*value="sf">' +
            r'San Francisco</option></select>')

        with app.test_client() as client:
            resp = client.get(f"/cafes/add")
            self.assertRegex(resp.data.decode('utf8'), choices_pattern)

            resp = client.get(f"/cafes/{id}/edit")
            self.assertRegex(resp.data.decode('utf8'), choices_pattern)

    def test_edit(self):
        id = self.cafe_id

        with app.test_client() as client:
            resp = client.get(f"/cafes/{id}/edit", follow_redirects=True)
            self.assertIn(b'Edit Test Cafe', resp.data)

            resp = client.post(
                f"/cafes/{id}/edit",
                data=CAFE_DATA_EDIT,
                follow_redirects=True)
            self.assertIn(b'edited', resp.data)

    def test_edit_form_shows_curr_data(self):
        id = self.cafe_id

        with app.test_client() as client:
            resp = client.get(f"/cafes/{id}/edit", follow_redirects=True)
            self.assertIn(b'Test description', resp.data)

    def test_get_choices(self):
        """ tests the get_choices class method in class City"""

        choices = City.get_choices()

        self.assertIn(('sf', 'San Francisco') , choices)



#######################################
# users


class UserModelTestCase(TestCase):
    """Tests for the user model."""

    def setUp(self):
        """Before each test, add sample users."""

        User.query.delete()

        user = User.register(**TEST_USER_DATA)

        db.session.commit()

        self.user = user

    def tearDown(self):
        """After each test, remove all users."""

        User.query.delete()
        db.session.commit()

    def test_authenticate(self):
        rez = User.authenticate("test", "secret")
        self.assertEqual(rez, self.user)

    def test_authenticate_fail(self):
        rez = User.authenticate("no-such-user", "secret")
        self.assertFalse(rez)

        rez = User.authenticate("test", "password")
        self.assertFalse(rez)

    def test_full_name(self):
        self.assertEqual(self.user.get_full_name(), "Testy MacTest")

    def test_register(self):
        u = User.register(**TEST_USER_DATA)
        # test that password gets bcrypt-hashed (all start w/$2b$)
        self.assertEqual(u.hashed_password[:4], "$2b$")
        db.session.rollback()


class AuthViewsTestCase(TestCase):
    """Tests for views on logging in/logging out/registration."""

    def setUp(self):
        """Before each test, add sample users."""

        User.query.delete()

        user = User.register(**TEST_USER_DATA)

        db.session.commit()

        self.user_id = user.id

    def tearDown(self):
        """After each test, remove all users."""

        User.query.delete()
        db.session.commit()

    def test_signup(self):
        with app.test_client() as client:
            resp = client.get("/signup")
            self.assertIn(b'Sign Up', resp.data)

            resp = client.post(
                "/signup",
                data=TEST_USER_DATA_NEW,
                follow_redirects=True,
            )

            self.assertIn(b"You are signed up and logged in.", resp.data)
            self.assertTrue(session.get(CURR_USER_KEY))

    def test_signup_username_taken(self):

        with app.test_client() as client:
            resp = client.get("/signup")
            self.assertIn(b'Sign Up', resp.data)

            # signup with same data as the already-added user
            resp = client.post(
                "/signup",
                data=TEST_USER_DATA,
                follow_redirects=True,
            )

            db.session.rollback()

            self.assertIn(b"Username already taken", resp.data)

    def test_login(self):
        with app.test_client() as client:
            resp = client.get("/login")
            self.assertIn(b'Welcome Back!', resp.data)

            resp = client.post(
                "/login",
                data={"username": "test", "password": "WRONG"},
                follow_redirects=True,
            )

            self.assertIn(b"Invalid credentials", resp.data)

            resp = client.post(
                "/login",
                data={"username": "test", "password": "secret"},
                follow_redirects=True,
            )

            self.assertIn(b"Hello, test", resp.data)
            self.assertEqual(session.get(CURR_USER_KEY), self.user_id)

    def test_logout(self):
        with app.test_client() as client:
            login_for_test(client, self.user_id)
            resp = client.post("/logout", follow_redirects=True)

            self.assertIn(b"successfully logged out", resp.data)
            self.assertEqual(session.get(CURR_USER_KEY), None)


class NavBarTestCase(TestCase):
    """Tests navigation bar."""

    def setUp(self):
        """Before tests, add sample user."""

        User.query.delete()

        user = User.register(**TEST_USER_DATA)

        db.session.add_all([user])
        db.session.commit()

        self.user_id = user.id

    def tearDown(self):
        """After tests, remove all users."""

        User.query.delete()
        db.session.commit()

    def test_anon_navbar(self):
        """ Tests that navbar only has access home, signup, and login tabs """
        with app.test_client() as client:

            resp = client.get('/')

            html = resp.get_data(as_text=True)

            self.assertIn("Sign up", html)
            self.assertIn("Log in", html)
            self.assertNotIn("Log Out", html)
            self.assertEqual(session.get(CURR_USER_KEY), None)


    def test_logged_in_navbar(self):
        """ Test that user's fullname and logout tab are in the navbar """
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id

            resp = client.get('/')

            html = resp.get_data(as_text=True)

            self.assertIn("Log out", html)
            self.assertNotIn("Sign up", html)
            self.assertNotIn("Log in", html)
            self.assertEqual(session.get(CURR_USER_KEY), self.user_id)


class ProfileViewsTestCase(TestCase):
    """Tests for views on user profiles."""

    def setUp(self):
        """Before each test, add sample user."""

        User.query.delete()

        user = User.register(**TEST_USER_DATA)
        db.session.add(user)

        db.session.commit()

        self.user_id = user.id

    def tearDown(self):
        """After each test, remove all users."""

        User.query.delete()
        db.session.commit()

    def test_anon_profile(self):
        """ Tests that user cannot access profile routes """
        with app.test_client() as client:

            resp = client.get('/profile',
                follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertIn('You are not logged in.', html)
            self.assertEqual(session.get(CURR_USER_KEY), None)

    def test_logged_in_profile(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id

            user = User.query.get_or_404(self.user_id)
            resp = client.get('/profile')

            html = resp.get_data(as_text=True)

            self.assertIn(user.get_full_name(), html)
            self.assertTrue(session.get(CURR_USER_KEY))

    def test_anon_profile_edit(self):
        """ Tests that user cannot access profile edit form """
        with app.test_client() as client:

            resp = client.get('/profile/edit',
                follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertIn('You are not logged in.', html)
            self.assertEqual(session.get(CURR_USER_KEY), None)

    def test_logged_in_profile_edit(self):
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id

            user = User.query.get_or_404(self.user_id)
            resp = client.post('/profile/edit',
                data=TEST_USER_DATA_EDIT,
                follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertIn(user.get_full_name(), html)
            self.assertTrue(session.get(CURR_USER_KEY))


#######################################
# likes


class LikeViewsTestCase(TestCase):
    """Tests for views on cafes."""

    def setUp(self):
        """Before each test, add sample user."""

        User.query.delete()
        Cafe.query.delete()
        City.query.delete()

        sf = City(**CITY_DATA)
        db.session.add(sf)

        cafe = Cafe(**CAFE_DATA)
        db.session.add(cafe)

        user = User.register(**TEST_USER_DATA)
        db.session.add(user)

        db.session.commit()

        self.cafe_id = cafe.id
        self.user_id = user.id

    def tearDown(self):
        """After each test, remove all users."""

        Like.query.delete()
        db.session.commit()

    def test_anon_liked_list(self):
        """ Test that anon user cannot access liked list in user's profile """
        with app.test_client() as client:
            resp = client.get("/profile", follow_redirects=True)

            html = resp.get_data(as_text=True)

            self.assertIn('You are not logged in.', html)
            self.assertFalse(session.get(CURR_USER_KEY))

    def test_logged_in_empty_likes(self):
        """ Test that logged in user can see empty likes list
        in their profile """

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id

            resp = client.get('/profile')

            html = resp.get_data(as_text=True)

            self.assertIn('You have no liked cafes.', html)
            self.assertTrue(session.get(CURR_USER_KEY))

    def test_logged_in_with_likes(self):
        """ Test that logged in user can see populated likes list
        in their profile """

        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user_id

            user=User.query.get_or_404(self.user_id)
            cafe=Cafe.query.get_or_404(self.cafe_id)

            user.liked_cafes.append(cafe)

            resp = client.get('/profile')

            html = resp.get_data(as_text=True)

            self.assertIn(cafe.name, html)
            self.assertTrue(session.get(CURR_USER_KEY))

