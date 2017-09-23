from flask_bcrypt import Bcrypt


# Create the Flask-Bcrypt's instance
from flask_cache import Cache
from flask_login import LoginManager
from flask_principal import Principal, Permission, RoleNeed

bcrypt = Bcrypt()

# Create the Flask-Principal's instance
principals = Principal()

# Create the Flask-Cache's instance
cache = Cache()

# Create the Flask-Login's instance
login_manager = LoginManager()
# Init the permission object via RoleNeed(Need).
admin_permission = Permission(RoleNeed('admin'))
poster_permission = Permission(RoleNeed('poster'))
default_permission = Permission(RoleNeed('default'))
# Setup the configuration for login manager.
#     1. Set the login page.
#     2. Set the more stronger auth-protection.
#     3. Show the information when you are logging.
#     4. Set the Login Messages type as `information`.
login_manager.login_view = "home.login"
login_manager.session_protection = "strong"
login_manager.login_message = ""
login_manager.login_message_category = "info"
# login_manager.anonymous_user = CustomAnonymousUser


@login_manager.user_loader
def load_user(user_id):
    """Load the user's info."""
    from webapp.models import User
    return User.query.filter_by(id=user_id).first()