from flask.ext.bcrypt import Bcrypt


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
login_manager.login_view = "main.login"
login_manager.session_protection = "strong"
login_manager.login_message = "Please login to access this page."
login_manager.login_message_category = "info"
# login_manager.anonymous_user = CustomAnonymousUser