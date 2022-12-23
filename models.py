"""Data models for Flask Cafe"""


from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy


bcrypt = Bcrypt()
db = SQLAlchemy()
DEFAULT_IMG_URL = "/static/images/default-cafe.jpg"

class City(db.Model):
    """Cities for cafes."""

    __tablename__ = 'cities'

    code = db.Column(
        db.Text,
        primary_key=True,
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    state = db.Column(
        db.String(2),
        nullable=False,
    )

    @classmethod
    def get_choices(self):
        """ returns list of tuples containing city code & name """

        return [(city.code, city.name) for city in City.query.all()]


class Cafe(db.Model):
    """Cafe information."""

    __tablename__ = 'cafes'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    name = db.Column(
        db.Text,
        nullable=False,
    )

    description = db.Column(
        db.Text,
        nullable=False,
    )

    url = db.Column(
        db.Text,
        nullable=False,
    )

    address = db.Column(
        db.Text,
        nullable=False,
    )

    city_code = db.Column(
        db.Text,
        db.ForeignKey('cities.code'),
        nullable=False,
    )

    image_url = db.Column(
        db.Text,
        nullable=False,
        default=DEFAULT_IMG_URL,
    )

    city = db.relationship("City", backref='cafes')

    def __repr__(self):
        return f'<Cafe id={self.id} name="{self.name}">'

    def get_city_state(self):
        """Return 'city, state' for cafe."""

        city = self.city
        return f'{city.name}, {city.state}'

class User(db.Model):
    """ User table """

    __tablename__ = 'users'

    id = db.Column(db.Integer,
        primary_key=True,
        autoincrement=True)

    username = db.Column(db.String(15),
        unique=True,
        nullable=False)

    admin = db.Column(db.Boolean,
        nullable=False)

    email = db.Column(db.String(50),
        unique=True,
        nullable=False)

    first_name = db.Column(db.String(30),
        nullable=False)

    last_name = db.Column(db.String(30),
        nullable=False)

    description = db.Column(db.Text)

    image_url = db.Column(db.Text,
        nullable=False,
        default=DEFAULT_IMG_URL)

    hashed_password = db.Column(db.Text,
        nullable=False)

    def get_full_name(self):
        """ returns string of full name """

        return f'{self.first_name} {self.last_name}'

    @classmethod
    def authenticate(cls, username, password):
        """ validates that password entered is equivalent to the hashed password
        in the database """

        user = User.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.hashed_password, password)
            if is_auth:
                return user

        return False

    @classmethod
    def register(cls, username, email, first_name, last_name,
    description, password, image_url=DEFAULT_IMG_URL):
        """ handles password hashiing and returns new user """

        #look into admin stuff from flask wrap up
        hashed_pw = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username = username,
            admin = False,
            email = email,
            first_name = first_name,
            last_name = last_name,
            description = description,
            image_url = image_url,
            hashed_password = hashed_pw
        )

        db.session.add(user)
        return user

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    app.app_context().push()
    db.app = app
    db.init_app(app)
