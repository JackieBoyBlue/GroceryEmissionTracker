import os, logging
from flask import Flask
from flask_dotenv import DotEnv
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_assets import Environment
from flask_login import LoginManager
from flask_caching import Cache
from flask_compress import Compress


# Initialisation and configuration for:
# Flask app
app = Flask(__name__)
env = DotEnv(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'secret_key')

app.url_map.strict_slashes = False

# Cookie security
cookie_security = True
app.config['SESSION_COOKIE_SECURE'] = cookie_security
app.config['REMEMBER_COOKIE_SECURE'] = cookie_security
app.config['REMEMBER_COOKIE_HTTPONLY'] = True


# Database connection
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '.db')
db = SQLAlchemy(app)


# Login and form protection
login_manager = LoginManager(app)
csrf = CSRFProtect(app)


# Assets
from .static.assets import bundles
assets = Environment(app)
assets.register(bundles)


# Logging
logging.basicConfig(
    filename="app/.log",
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(message)s'
)


# Caching & Compression
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})
cache.init_app(app)
Compress(app)


# Routing
from .routes import auth, starling, user


# Initialise Database
from .models import user, transaction, estimate
with app.app_context():
    db.create_all()

    # Create admin user if none exists
    if user.User.query.count() == 0:
        admin_name=os.getenv('ADMIN_NAME', 'admin')
        admin_email=os.getenv('ADMIN_EMAIL', 'admin')
        admin_password=os.getenv('ADMIN_PASSWORD', 'admin')
        user = user.User(
            name=admin_name,
            email=admin_email,
            password=admin_password,
            admin=True
        )
        db.session.add(user)
        db.session.commit()
    
    # Create category emission factors if none exist
    if estimate.GroceryItem.query.count() == 0:
        print('Generating category emission factors...')
        from .datasets.item_emission_factors import emission_factors
        from .models.embedding import model
        for item, factor in emission_factors.items():
            embedded = model.get_embeddings(item)[0]

            item = estimate.GroceryItem(
                name=item,
                factor=factor,
                vector=embedded
            )
            db.session.add(item)
            print(f'{item.name} added to database.')
        db.session.commit()
        print('Finished generating category emission factors.')

