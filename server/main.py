from flask import Flask, render_template
import requests
import logging
from database import db

from resources.artists import artists_bp
from resources.albums import albums_bp
from resources.tracks import tracks_bp
from resources.users import users_bp
from resources.playlists import playlists_bp
from resources.search import search_bp

app = Flask(__name__)
app.logger.setLevel(logging.ERROR)
app.url_map.strict_slashes = False
app.json.ensure_ascii = False  # Support Turkish characters

# Register Blueprints
artists_bp.register_blueprint(tracks_bp)
artists_bp.register_blueprint(albums_bp)
users_bp.register_blueprint(playlists_bp)
app.register_blueprint(search_bp, url_prefix="/api/")
app.register_blueprint(artists_bp, url_prefix="/api/")
app.register_blueprint(users_bp, url_prefix="/api/")

# Routes for the website
@app.route("/")
def HomePage():
    # Fetching artists and tracks from API endpoints
    try:
        artists_response = requests.get("http://localhost:5000/api/artists").json()
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching data: {e}")
        artists_response = []

    return render_template(
        "homepage.html",
        title="Home",
        artists=artists_response,
    )

@app.route("/artists/<int:artist_id>")
def ArtistDetailsPage(artist_id):
    try:
        # Fetch artist details from the API
        artist_response = requests.get(f"http://localhost:5000/api/artists/{artist_id}").json()
        albums_response = requests.get(f"http://localhost:5000/api/artists/{artist_id}/albums").json()
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching artist data: {e}")
        artist_response = {}
        albums_response = []

    if not artist_response:
        return render_template("404.html", title="Artist Not Found"), 404

    return render_template(
        "artist_details.html",
        title=artist_response.get("name", "Artist Details"),
        artist=artist_response,
        albums=albums_response,
    )
@app.route("/artists/<int:artist_id>/albums/<int:album_id>")
def AlbumDetailsPage(album_id,artist_id):
    try:
        # Fetch album details and tracks from the API
        album_response = requests.get(f"http://localhost:5000/api/albums/{album_id}").json()
        tracks_response = requests.get(f"http://localhost:5000/api/artists/{artist_id}/albums/{album_id}").json()
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching album data: {e}")
        album_response = {}
        tracks_response = []

    if not album_response:
        return render_template("404.html", title="Album Not Found"), 404

    return render_template(
        "album_details.html",
        title=album_response.get("name", "Album Details"),
        album=album_response,
        tracks=tracks_response,
    )


if __name__ == "__main__":
    db()
    app.run(host="0.0.0.0", port=5000, debug=True)
