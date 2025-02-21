from flask import Flask, session, redirect, url_for, request, render_template
import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler

app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(64)

# Set redirect URI based on environment
redirect_uri = (
    "https://encstats.vercel.app/callback"
    if os.getenv("FLASK_ENV") == "production"
    else "http://127.0.0.1:5000/callback"
)

# Spotify API credentials (Use environment variables)
client_id = "da6a918341704836931958964e9f8cf9"
client_secret = "f8e8786b555d446aa2cb28e3800234e3"
scope = "user-read-private user-read-email user-top-read user-read-recently-played user-library-read user-library-modify user-read-playback-state user-modify-playback-state"

cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
    client_id,
    client_secret,
    redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True,
)


@app.route("/")
def home():
    """Render home.html where user can click login."""
    return render_template("home.html")


@app.route("/login")
def login():
    """Redirect to Spotify login."""
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)


@app.route("/callback")
def callback():
    """Handle Spotify OAuth callback and store the token."""
    session["token_info"] = sp_oauth.get_access_token(request.args["code"])
    return redirect(url_for("data"))


@app.route("/data")
def data():
    """Display user data after successful login."""
    token_info = session.get("token_info", None)
    if not token_info:
        return redirect(url_for("home"))  # Redirect to home if not logged in

    sp = Spotify(auth=token_info["access_token"])
    user = sp.current_user()
    top_songs = sp.current_user_top_tracks(limit=10)["items"]
    top_artists = sp.current_user_top_artists(limit=10)["items"]
    top_albums = sp.current_user_saved_albums(limit=10)["items"]
    return render_template(
        "data.html",
        user=user,
        top_songs=top_songs,
        top_artists=top_artists,
        top_albums=top_albums,
    )


@app.route("/logout")
def logout():
    """Log out and clear session."""
    session.clear()
    return redirect(url_for("home"))


@app.route("/artists")
def artists():
    """Display top artists."""
    token_info = session.get("token_info", None)
    if not token_info:
        return redirect(url_for("home"))
    sp = Spotify(auth=token_info["access_token"])
    user = sp.current_user()
    top_artists = sp.current_user_top_artists(limit=10)["items"]

    return render_template("artists.html", user=user, top_artists=top_artists)


@app.route("/search")
def search():
    return render_template("search.html")


if __name__ == "__main__":
    app.run(debug=True)
