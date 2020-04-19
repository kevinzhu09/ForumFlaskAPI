# https://requests-oauthlib.readthedocs.io/en/latest/index.html

import requests
from flask_jwt_extended import create_access_token
from requests_oauthlib import OAuth2Session
from flask import request, redirect, session, Blueprint
from routes.data_access.users_data_access import login_social_user

from config.APIConfig import APP_URI, TOKEN_TTL_TIMEDELTA, google_data

from werkzeug.local import LocalProxy
from flask import current_app

logger = LocalProxy(lambda: current_app.logger)

google_routes = Blueprint('google_routes', __name__)

# https://developers.google.com/identity/protocols/oauth2/openid-connect

client_id = google_data['GOOGLE_CLIENT_ID']
client_secret = google_data['GOOGLE_CLIENT_SECRET']

GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()

authorization_endpoint = google_provider_cfg["authorization_endpoint"]
token_endpoint = google_provider_cfg["token_endpoint"]
profile_endpoint = google_provider_cfg["userinfo_endpoint"]


@google_routes.route("/api/google/login", methods=['GET'])
def google_login():
    """Step 1: User Authorization.

    Redirect the user/resource owner to the OAuth provider (i.e. google_routes)
    using an URL with a few key OAuth parameters.
    """
    google = OAuth2Session(client_id, scope=["openid", "email", "profile"], redirect_uri=request.base_url + '/callback')
    authorization_url, state = google.authorization_url(authorization_endpoint)

    # State is used to prevent CSRF, keep this for later.
    session['oauth_state'] = state
    return redirect(authorization_url)


# Step 2: User authorization, this happens on the provider.

@google_routes.route("/api/google/login/callback", methods=["GET"])
def google_callback():
    """ Step 3: Retrieving an access token.

    The user has been redirected back from the provider to your registered
    callback URL. With this redirection comes an authorization code included
    in the redirect URL. We will use that to obtain an access token.
    """

    if request.args.get("state") != session['oauth_state']:
        logger.error("Invalid state")
        return redirect(APP_URI + "/error-page")

    fetch_auth_session = OAuth2Session(client_id, redirect_uri=request.base_url)
    google_token = fetch_auth_session.fetch_token(token_endpoint, client_secret=client_secret,
                                                  authorization_response=request.url)

    """Fetching a protected resource using an OAuth 2 token.
    """
    user_auth_session = OAuth2Session(client_id, token=google_token)
    google_user = user_auth_session.get(profile_endpoint).json()
    if google_user["email_verified"]:
        username = google_user["name"]
        email = google_user["email"]
        user_id = login_social_user(google_user["sub"], email, 'Google', username)
        jwt_token = create_access_token(identity={"user_id": user_id}, expires_delta=TOKEN_TTL_TIMEDELTA)
        return redirect(APP_URI + "/logged-in?token=" + jwt_token)
    else:
        logger.error("Email not verified")
        return redirect(APP_URI + "/error-page")
