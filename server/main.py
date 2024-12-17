from flask import Flask, render_template, request, redirect, flash, url_for, session

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

app.secret_key = "1234"

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
def AlbumDetailsPage(artist_id, album_id):
    try:
        # Fetch album details and tracks from the API
        artist_response = requests.get(f"http://localhost:5000/api/artists/{artist_id}").json()
        album_response = requests.get(f"http://localhost:5000/api/artists/{artist_id}/albums/{album_id}").json()
        tracks_response = requests.get(f"http://localhost:5000/api/artists/{artist_id}/albums/{album_id}/tracks").json()

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching album data: {e}")
        album_response = {}
        tracks_response = []

    if not album_response:
        return render_template("404.html", title="Not Found"), 404

    return render_template(
        "album_details.html",
        title=album_response.get("name", "Album Details"),
        artist=artist_response,
        album=album_response,
        tracks=tracks_response,
    )

@app.route("/artists/<int:artist_id>/albums/<int:album_id>/tracks/<int:track_id>/likes", methods=["GET"])
def TrackLikesPage(artist_id, album_id, track_id):
    try:
        # Fetch users who liked this track
        likes_response = requests.get(
            f"http://localhost:5000/api/artists/{artist_id}/albums/{album_id}/tracks/{track_id}/likes"
        ).json()
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching likes: {e}")
        likes_response = []

    return render_template(
        "track_likes.html",
        title="Track Likes",
        track_id=track_id,
        likes=likes_response
    )


@app.route("/artists/<int:artist_id>/albums/<int:album_id>/tracks/<int:track_id>/rates", methods=["GET"])
def TrackRatesPage(artist_id, album_id, track_id):
    try:
        # Fetch ratings for this track
        rates_response = requests.get(
            f"http://localhost:5000/api/artists/{artist_id}/albums/{album_id}/tracks/{track_id}/rates"
        ).json()
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching rates: {e}")
        rates_response = []

    return render_template(
        "track_rates.html",
        title="Track Ratings",
        track_id=track_id,
        artist_id=artist_id,
        album_id=album_id,
        rates=rates_response
    )

@app.route("/artists", methods=["GET"])
def ExploreArtistsPage():
    try:
        search_query = request.args.get("q", "")

        if search_query:
            response = requests.get(
                "http://localhost:5000/api/search",
                params={
                    "q": search_query,
                    "filter": "artist",
                },
            )
            artists_response = response.json().get("result", [])
        else:
            artists_response = []

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching artists: {e}")
        artists_response = []

    return render_template(
        "explore_artists.html",
        title="Explore Artists",
        artists=artists_response,
        search_query=search_query,
    )

@app.route("/albums", methods=["GET"])
def ExploreAlbumsPage():
    try:
        # Get search query
        search_query = request.args.get("q", "")

        # Fetch albums via the search API
        if search_query:
            response = requests.get(
                "http://localhost:5000/api/search",
                params={
                    "q": search_query,
                    "filter": "album",
                },
            )
            albums_response = response.json().get("result", [])
        else:
            # Default fetch if no search query
            response = requests.get("http://localhost:5000/api/albums")
            albums_response = response.json()

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching albums: {e}")
        albums_response = []

    return render_template(
        "explore_albums.html",
        title="Explore Albums",
        albums=albums_response,
        search_query=search_query,
    )

@app.route("/tracks", methods=["GET"])
def ExploreTracksPage():
    try:
        # Get search query
        search_query = request.args.get("q", "")

        # Fetch tracks via the search API
        if search_query:
            response = requests.get(
                "http://localhost:5000/api/search",
                params={
                    "q": search_query,
                    "filter": "track",
                },
            )
            tracks_response = response.json().get("result", [])
        else:
            # Default fetch if no search query
            response = requests.get("http://localhost:5000/api/tracks")
            tracks_response = response.json()

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching tracks: {e}")
        tracks_response = []

    return render_template(
        "explore_tracks.html",
        title="Explore Tracks",
        tracks=tracks_response,
        search_query=search_query,
    )

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nickname = request.form.get("nickname")
        email = request.form.get("email")
        gender = request.form.get("gender")

        if not nickname or not email or not gender:
            flash("All fields are required.", "error")
            return render_template("register.html")

        response = requests.post(
            "http://localhost:5000/api/users",
            json={"nickname": nickname, "email": email, "gender": gender},
        )

        if response.status_code == 201:
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("login"))
        else:
            error = response.json().get("error", "Registration failed.")
            flash(error, "error")
            return render_template("register.html")

    return render_template("register.html")



from flask import session, flash, redirect, url_for

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        nickname = request.form.get("nickname")

        if not email or not nickname:
            flash("Both email and nickname are required.", "error")
            return render_template("login.html")

        try:
            # Fetch all users from the API
            response = requests.get("http://localhost:5000/api/users")
            if response.status_code != 200:
                flash("Internal server error. Please try again.", "error")
                return render_template("login.html")

            users = response.json()

            # Validate user credentials
            for user in users:
                if user["email"] == email and user["nickname"] == nickname:
                    session["user_id"] = user["id"]
                    session["nickname"] = user["nickname"]
                    flash("Login successful!", "success")
                    return redirect(url_for("HomePage"))

            flash("Invalid email or nickname. Please try again.", "error")
            return render_template("login.html")

        except Exception as e:
            print(f"Error: {e}")
            flash("An error occurred while logging in. Please try again.", "error")
            return render_template("login.html")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("HomePage"))

@app.route("/playlists", methods=["GET", "POST"])
def user_playlists():
    if "user_id" not in session:
        flash("You need to log in to access your playlists.", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]

    try:
        # Fetch playlists
        response = requests.get(f"http://localhost:5000/api/users/{user_id}/playlists")
        if response.status_code != 200:
            flash("Could not fetch playlists. Try again later.", "error")
            return redirect(url_for("HomePage"))

        playlists = response.json()

        if request.method == "POST":
            action = request.form.get("action")
            playlist_id = request.form.get("playlist_id")
            track_id = request.form.get("track_id")

            if not playlist_id or not track_id:
                flash("Playlist ID and Track ID are required.", "error")
                return redirect(url_for("user_playlists"))

            # Add or remove track based on form action
            if action == "add":
                add_response = requests.post(
                    f"http://localhost:5000/api/users/{user_id}/playlists/{playlist_id}/add",
                    json={"track_id": track_id},
                )
                if add_response.status_code == 201:
                    flash("Track added successfully!", "success")
                else:
                    flash("Failed to add track. Try again.", "error")
            elif action == "remove":
                remove_response = requests.post(
                    f"http://localhost:5000/api/users/{user_id}/playlists/{playlist_id}/remove",
                    json={"track_id": track_id},
                )
                if remove_response.status_code == 200:
                    flash("Track removed successfully!", "success")
                else:
                    flash("Failed to remove track. Try again.", "error")

            return redirect(url_for("user_playlists"))

        return render_template("playlists.html", playlists=playlists)

    except Exception as e:
        print(f"Error: {e}")
        flash("An error occurred while managing playlists.", "error")
        return redirect(url_for("HomePage"))
