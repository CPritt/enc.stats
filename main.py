from flask import Flask, session, redirect, url_for, request, render_template
import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler


app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(64)

redirect_uri = "https://encstats.vercel.app/callback"

# redirect_uri = "http://127.0.0.1:5000/callback"  


client_id = "da6a918341704836931958964e9f8cf9"
client_secret = "f8e8786b555d446aa2cb28e3800234e3"
scope = "user-read-private user-read-email user-top-read user-read-recently-played user-library-read user-library-modify user-read-playback-state user-modify-playback-state"

cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
    client_id, client_secret, redirect_uri, scope=scope, cache_handler=cache_handler, show_dialog=True
)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/login")
def login():
    """Redirect to Spotify login."""
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route("/callback")
def callback():
    try:
        code = request.args.get("code")
        if not code:
            return "Error: No authorization code provided", 400

        token_info = sp_oauth.get_access_token(code)
        session["token_info"] = token_info  # Store in session

        return redirect(url_for("get_data"))

    except Exception as e:
        return f"Callback Error: {str(e)}", 500

@app.route("/get_data")
def get_data():
    try:
        token_info = session.get("token_info")
        if not token_info:
            return redirect(url_for("home"))

        sp = Spotify(auth=token_info["access_token"])  # Ensure token is valid
        user = sp.current_user()
        top_songs = sp.current_user_top_tracks(limit=10)["items"]
        top_albums = [album["album"] for album in sp.current_user_saved_albums(limit=10)["items"]]
        top_artists = sp.current_user_top_artists(limit=10)["items"]

        return render_template("data.html", user=user, top_songs=top_songs, top_albums=top_albums, top_artists=top_artists)

    except Exception as e:
        return f"Error fetching user data: {str(e)}", 500

@app.route("/logout")
def logout():
    """Log out and clear session."""
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
