from functools import wraps

from flask import request, Response, current_app


def check_auth(username, password):
    """
    This function is called to check if a username / password combination
    is valid.
    """
    check_username = username == current_app.config['AUTH_USERNAME']
    check_password = password == current_app.config['AUTH_PASSWORD']

    return check_username and check_password


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response('Could not verify your access level for that URL.\n'
                    'You have to login with proper credentials', 401,
                    {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
