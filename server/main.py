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

@app.route("/artists/<int:artist_id>", methods=["GET", "POST"])
def ArtistDetailsPage(artist_id):
    try:
        # Fetch artist details and albums
        artist_response = requests.get(f"http://localhost:5000/api/artists/{artist_id}").json()
        albums_response = requests.get(f"http://localhost:5000/api/artists/{artist_id}/albums").json()

        # POST actions
        if request.method == "POST":
            action = request.form.get("action")
            album_id = request.form.get("album_id")
            album_name = request.form.get("album_name")
            album_type = request.form.get("album_type")
            release_date = request.form.get("release_date")

            
            # Create album
            if action == "create_album":
                if not album_name or not album_type or not release_date:
                    flash("Album name, type, and release date are required.", "error")
                else:
                    create_response = requests.post(
                        f"http://localhost:5000/api/artists/{artist_id}/albums",
                        json={
                            "name": album_name,
                            "type": album_type,
                            "release_date": release_date,
                        },
                    )
                    if create_response.status_code == 201:
                        flash("Album created successfully!", "success")
                    else:
                        flash("Failed to create album. Try again.", "error")

            # Edit album
            elif action == "edit_album":
                if not album_id or not album_name or not album_type or not release_date:
                    flash("Album ID, name, type, and release date are required.", "error")
                else:
                    edit_response = requests.put(
                        f"http://localhost:5000/api/artists/{artist_id}/albums/{album_id}",
                        json={
                            "name": album_name,
                            "type": album_type,
                            "release_date": release_date,
                        },
                    )
                    if edit_response.status_code == 200:
                        flash("Album updated successfully!", "success")
                    else:
                        flash("Failed to update album. Try again.", "error")
                        
            # Delete artist
            elif action == "delete_artist":
                delete_response = requests.delete(f"http://localhost:5000/api/artists/{artist_id}")
                if delete_response.status_code == 200:
                    flash("Artist deleted successfully!", "success")
                    return redirect(url_for("ExploreArtistsPage"))
                else:
                    flash("Failed to delete artist. Try again.", "error")
            
            # Delete album
            elif action == "delete_album":
                if not album_id:
                    flash("Album ID is required for deletion.", "error")
                else:
                    delete_response = requests.delete(
                        f"http://localhost:5000/api/artists/{artist_id}/albums/{album_id}"
                    )
                    if delete_response.status_code == 200:
                        flash("Album deleted successfully!", "success")
                    else:
                        flash("Failed to delete album. Try again.", "error")

            return redirect(url_for("ArtistDetailsPage", artist_id=artist_id))

        return render_template(
            "artist_details.html",
            title=artist_response.get("name", "Artist Details"),
            artist=artist_response,
            albums=albums_response,
        )

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching artist data: {e}")
        flash("An error occurred. Please try again later.", "error")
        return redirect(url_for("ExploreArtistsPage"))


@app.route("/artists/<int:artist_id>/albums/<int:album_id>", methods=["GET", "POST"])
def AlbumDetailsPage(artist_id, album_id):
    try:
        # Handle POST actions for adding, editing, or removing tracks
        if request.method == "POST":
            action = request.form.get("action")
            track_id = request.form.get("track_id")
            track_name = request.form.get("track_name")
            length_sec = request.form.get("length_sec")

            # Add track
            if action == "add_track":
                if not track_name or not length_sec:
                    flash("Track name and length are required to add a track.", "error")
                else:
                    add_response = requests.post(
                        f"http://localhost:5000/api/artists/{artist_id}/albums/{album_id}/tracks",
                        json={"name": track_name, "length_sec": length_sec},
                    )
                    if add_response.status_code == 201:
                        flash("Track added successfully!", "success")
                    else:
                        flash("Failed to add track. Try again.", "error")

            # Edit track
            elif action == "edit_track":
                if not track_id or not track_name or not length_sec:
                    flash("Track ID, name, and length are required to edit a track.", "error")
                else:
                    edit_response = requests.put(
                        f"http://localhost:5000/api/tracks/{track_id}",
                        json={"name": track_name, "length_sec": length_sec},
                    )
                    if edit_response.status_code == 200:
                        flash("Track updated successfully!", "success")
                    else:
                        flash("Failed to update track. Try again.", "error")

            # Remove track
            elif action == "remove_track":
                if not track_id:
                    flash("Track ID is required to remove a track.", "error")
                else:
                    remove_response = requests.delete(
                        f"http://localhost:5000/api/tracks/{track_id}"
                    )
                    if remove_response.status_code == 200:
                        flash("Track removed successfully!", "success")
                    else:
                        flash("Failed to remove track. Try again.", "error")

            # Like track
            elif action == "like_track":
                user_id = session.get("user_id")
                if not user_id:
                    flash("You need to log in to like a track.", "error")
                else:
                    like_response = requests.post(
                        f"http://localhost:5000/api/tracks/{track_id}/likes",
                        json={"user_id": user_id},
                    )
                    if like_response.status_code == 200:
                        flash("Track liked successfully!", "success")
                    else:
                        flash("Failed to like track. Try again.", "error")

            # Unlike track
            elif action == "unlike_track":
                user_id = session.get("user_id")
                if not user_id:
                    flash("You need to log in to unlike a track.", "error")
                else:
                    unlike_response = requests.delete(
                        f"http://localhost:5000/api/tracks/{track_id}/likes",
                        json={"user_id": user_id},
                    )
                    if unlike_response.status_code == 200:
                        flash("Track unliked successfully!", "success")
                    else:
                        flash("Failed to unlike track. Try again.", "error")

            # Rate track
            elif action == "rate_track":
                user_id = session.get("user_id")
                new_rating = request.form.get("rating")
                if not user_id or not new_rating:
                    flash("Rating and login are required to rate a track.", "error")
                else:
                    rate_response = requests.post(
                        f"http://localhost:5000/api/tracks/{track_id}/rates",
                        json={"rate": int(new_rating), "user_id": user_id},
                    )
                    if rate_response.status_code == 409:
                        rate_response = requests.patch(
                            f"http://localhost:5000/api/tracks/{track_id}/rates",
                            json={"rate": int(new_rating), "user_id": user_id},
                        )
                    if rate_response.status_code == 200:
                        flash("Track rating updated successfully!", "success")
                    else:
                        flash("Failed to rate track. Try again.", "error")

            return redirect(url_for("AlbumDetailsPage", artist_id=artist_id, album_id=album_id))

        # Fetch artist, album, and tracks details
        artist_response = requests.get(f"http://localhost:5000/api/artists/{artist_id}").json()
        album_response = requests.get(f"http://localhost:5000/api/artists/{artist_id}/albums/{album_id}").json()
        tracks_response = requests.get(f"http://localhost:5000/api/artists/{artist_id}/albums/{album_id}/tracks").json()

        # Check for album existence
        if not album_response:
            return render_template("404.html", title="Not Found"), 404

        # Fetch likes and rates for each track
        for track in tracks_response:
            track_id = track["id"]

            # Fetch likes for the track
            likes_response = requests.get(f"http://localhost:5000/api/tracks/{track_id}/likes").json()
            track["likes"] = likes_response.get("like_count", 0) if isinstance(likes_response, dict) else 0

            # Fetch rates for the track
            rates_response = requests.get(f"http://localhost:5000/api/tracks/{track_id}/rates").json()
            track["avg_rate"] = rates_response.get("average_rate", 0.0) if isinstance(rates_response, dict) else 0.0

        return render_template(
            "album_details.html",
            title=album_response.get("name", "Album Details"),
            artist=artist_response,
            album=album_response,
            tracks=tracks_response,
        )

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching album data: {e}")
        return render_template("500.html", title="Internal Server Error"), 500


@app.route("/artists", methods=["GET", "POST"])
def ExploreArtistsPage():
    try:
        # Fetch search query
        search_query = request.args.get("q", "")
        if search_query:
            response = requests.get(
                "http://localhost:5000/api/search",
                params={"q": search_query, "filter": "artist"},
            )
            artists = response.json().get("result", [])
        else:
            response = requests.get("http://localhost:5000/api/artists")
            artists = response.json()

        # Handle POST for creating a new artist
        if request.method == "POST":
            action = request.form.get("action")
            if action == "create_artist":
                name = request.form.get("name")
                short_info = request.form.get("short_info")
                create_response = requests.post(
                    "http://localhost:5000/api/artists",
                    json={"name": name, "short_info": short_info},
                )
                if create_response.status_code == 201:
                    flash("Artist created successfully!", "success")
                else:
                    flash("Failed to create artist. Try again.", "error")
                return redirect(url_for("ExploreArtistsPage"))

            elif action == "delete_artist":
                artist_id = request.form.get("artist_id")
                delete_response = requests.delete(f"http://localhost:5000/api/artists/{artist_id}")
                if delete_response.status_code == 200:
                    flash("Artist deleted successfully!", "success")
                else:
                    flash("Failed to delete artist. Try again.", "error")
                return redirect(url_for("ExploreArtistsPage"))

            elif action == "update_artist":
                artist_id = request.form.get("artist_id")
                name = request.form.get("name")
                short_info = request.form.get("short_info")
                update_response = requests.put(
                    f"http://localhost:5000/api/artists/{artist_id}",
                    json={"name": name, "short_info": short_info},
                )
                if update_response.status_code == 200:
                    flash("Artist updated successfully!", "success")
                else:
                    flash("Failed to update artist. Try again.", "error")
                return redirect(url_for("ExploreArtistsPage"))

    except requests.exceptions.RequestException as e:
        app.logger.error(f"Error fetching artists: {e}")
        artists = []

    return render_template(
        "explore_artists.html",
        title="Explore Artists",
        artists=artists,
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

@app.route("/tracks", methods=["GET", "POST"])
def ExploreTracksPage():
    try:
        # Get search query
        search_query = request.args.get("q", "")

        # Fetch tracks
        if search_query:
            response = requests.get(
                "http://localhost:5000/api/search",
                params={"q": search_query, "filter": "track"},
            )
            tracks_response = response.json().get("result", [])
        else:
            response = requests.get("http://localhost:5000/api/tracks")
            tracks_response = response.json()
        
        # Process tracks to include likes and average rating
        for track in tracks_response:
            # Fetch likes
            likes_response = requests.get(
                f"http://localhost:5000/api/artists/{track['artist_id']}/albums/{track['album_id']}/tracks/{track['id']}/likes"
            )
            if likes_response.status_code == 200 and isinstance(likes_response.json(), list):
                track["likes"] = likes_response.json()[0].get("like_count", 0)
            else:
                track["likes"] = 0

            # Fetch average rating
            rates_response = requests.get(
                f"http://localhost:5000/api/artists/{track['artist_id']}/albums/{track['album_id']}/tracks/{track['id']}/rates"
            )
            if rates_response.status_code == 200 and isinstance(rates_response.json(), dict):
                track["avg_rate"] = rates_response.json().get("average_rate", "N/A")
            else:
                track["avg_rate"] = "N/A"

        # Handle POST actions
        if request.method == "POST":
            action = request.form.get("action")
            track_id = request.form.get("track_id")
            artist_id = request.form.get("artist_id")
            album_id = request.form.get("album_id")

            # Edit track
            if action == "edit":
                new_name = request.form.get("track_name")
                new_length = request.form.get("length_sec")
                if not track_id or not new_name or not new_length:
                    flash("All fields are required to edit a track.", "error")
                else:
                    edit_response = requests.patch(
                        f"http://localhost:5000/api/artists/{artist_id}/albums/{album_id}/tracks/{track_id}",
                        json={"name": new_name, "length_sec": new_length},
                    )
                    if edit_response.status_code == 200:
                        flash("Track updated successfully!", "success")
                    else:
                        flash("Failed to update track. Try again.", "error")

            # Delete track
            elif action == "delete":
                if not track_id:
                    flash("Track ID is required to delete a track.", "error")
                else:
                    delete_response = requests.delete(
                        f"http://localhost:5000/api/artists/{artist_id}/albums/{album_id}/tracks/{track_id}"
                    )
                    if delete_response.status_code == 200:
                        flash("Track deleted successfully!", "success")
                    else:
                        flash("Failed to delete track. Try again.", "error")

            # Add like
            elif action == "like":
                user_id = session["user_id"]
                like_response = requests.post(
                    f"http://localhost:5000/api/artists/{artist_id}/albums/{album_id}/tracks/{track_id}/likes",
                    json={"user_id": user_id},
                )   

                if like_response.status_code == 200:
                    flash("Track liked successfully!", "success")
                else:
                    flash("Failed to like track. Try again.", "error")

            # Remove like
            elif action == "unlike":
                user_id = session["user_id"]
                unlike_response = requests.delete(
                    f"http://localhost:5000/api/artists/{artist_id}/albums/{album_id}/tracks/{track_id}/likes",
                    json={"user_id": user_id}
                )
                if unlike_response.status_code == 200:
                    flash("Track unliked successfully!", "success")
                else:
                    flash("Failed to unlike track. Try again.", "error")

            # Update rating
            elif action == "rate":
                new_rating = request.form.get("rating")
                user_id = session["user_id"]
                if not new_rating:
                    flash("Rating is required.", "error")
                else:
                    rate_response = requests.post(
                        f"http://localhost:5000/api/artists/{artist_id}/albums/{album_id}/tracks/{track_id}/rates",
                        json={"rate": int(new_rating), "user_id": user_id},
                    )
                    if rates_response.status_code == 409:
                        rate_response = requests.patch(
                        f"http://localhost:5000/api/artists/{artist_id}/albums/{album_id}/tracks/{track_id}/rates",
                        json={"rate": int(new_rating), "user_id": user_id},
                    )
                    if rate_response.status_code == 200:
                        flash("Track rating updated successfully!", "success")
                    else:
                        flash(rate_response.json().get("error", []), "error")

            # Redirect back with the search query
            return redirect(url_for("ExploreTracksPage", q=search_query))

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
        # Utility function to fetch all playlists
        def fetch_playlists():
            response = requests.get(f"http://localhost:5000/api/users/{user_id}/playlists")
            if response.status_code == 200:
                return response.json()
            return []

        # Utility function to fetch a specific playlist with its tracks
        def fetch_playlist_with_tracks(playlist_id):
            response = requests.get(f"http://localhost:5000/api/users/{user_id}/playlists/{playlist_id}")
            if response.status_code == 200:
                return response.json().get("playlist", {})
            return {}

        # Fetch playlists initially
        playlists = fetch_playlists()

        # Handle search query for tracks
        search_query = request.args.get("q", "")
        search_results = []
        if search_query:
            search_response = requests.get(
                f"http://localhost:5000/api/search",
                params={
                    "q": search_query,
                    "filter": "track",
                    "order_by": "asc",
                    "limit": 10,
                },
            )
            if search_response.status_code == 200:
                search_results = search_response.json().get("result", [])

        # Handle form submissions
        if request.method == "POST":
            action = request.form.get("action")
            playlist_name = request.form.get("playlist_name")
            playlist_id = request.form.get("playlist_id")
            track_id = request.form.get("track_id")

            # Create a new playlist
            if action == "create_playlist":
                if not playlist_name:
                    flash("Playlist name is required.", "error")
                else:
                    create_response = requests.post(
                        f"http://localhost:5000/api/users/{user_id}/playlists",
                        json={"name": playlist_name},
                    )
                    if create_response.status_code == 200:
                        flash("Playlist created successfully!", "success")
                        playlists = fetch_playlists()
                    else:
                        flash("Failed to create playlist. Try again.", "error")

            # Add a track to a playlist
            elif action == "add":
                if not playlist_id or not track_id:
                    flash("Playlist ID and Track ID are required.", "error")
                else:
                    add_response = requests.post(
                        f"http://localhost:5000/api/users/{user_id}/playlists/{playlist_id}",
                        json={"track_id": track_id},
                    )
                    if add_response.status_code == 201:
                        flash("Track added to playlist successfully!", "success")
                    else:
                        flash("Failed to add track. Try again.", "error")

            # Delete a playlist
            elif action == "delete_playlist":
                if not playlist_id:
                    flash("Playlist ID is required.", "error")
                else:
                    delete_response = requests.delete(
                        f"http://localhost:5000/api/users/{user_id}/playlists/{playlist_id}"
                    )
                    if delete_response.status_code == 200:
                        flash("Playlist deleted successfully!", "success")
                        playlists = fetch_playlists()
                    else:
                        flash("Failed to delete playlist. Try again.", "error")

            # Redirect back to the same page with the search query preserved
            return redirect(url_for("user_playlists", q=search_query))

        # Render the playlists page
        return render_template(
            "playlists.html", playlists=playlists, search_results=search_results, search_query=search_query
        )

    except Exception as e:
        app.logger.error(f"Error managing playlists: {e}")
        flash("An error occurred. Please try again.", "error")
        return redirect(url_for("HomePage"))

@app.route("/playlists/<int:playlist_id>", methods=["GET", "POST"])
def playlist_details(playlist_id):
    if "user_id" not in session:
        flash("You need to log in to view playlists.", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]

    try:
        # Handle POST actions for adding/removing tracks
        if request.method == "POST":
            action = request.form.get("action")
            track_id = request.form.get("track_id")

            if action == "add_track":
                if not track_id:
                    flash("Track ID is required to add a track.", "error")
                else:
                    add_response = requests.post(
                        f"http://localhost:5000/api/users/{user_id}/playlists/{playlist_id}",
                        json={"track_id": track_id},
                    )
                    if add_response.status_code == 201:
                        flash("Track added successfully!", "success")
                    else:
                        flash("Failed to add track. Try again.", "error")

            elif action == "remove_track":
                if not track_id:
                    flash("Track ID is required to remove a track.", "error")
                else:
                    remove_response = requests.delete(
                        f"http://localhost:5000/api/users/{user_id}/playlists/{playlist_id}/tracks/{track_id}"
                    )
                    if remove_response.status_code == 200:
                        flash("Track removed successfully!", "success")
                    else:
                        flash("Failed to remove track. Try again.", "error")

            return redirect(url_for("playlist_details", playlist_id=playlist_id))

        # Fetch playlist details and search results for adding tracks
        response = requests.get(f"http://localhost:5000/api/users/{user_id}/playlists/{playlist_id}")
        if response.status_code != 200:
            flash("Could not fetch playlist details. Try again.", "error")
            return redirect(url_for("user_playlists"))

        playlist = response.json().get("playlist", {})
        search_query = request.args.get("q", "")
        search_results = []

        if search_query:
            search_response = requests.get(
                f"http://localhost:5000/api/search",
                params={"q": search_query, "filter": "track", "limit": 10},
            )
            if search_response.status_code == 200:
                search_results = search_response.json().get("result", [])

        return render_template(
            "songs_detail.html", playlist=playlist, search_query=search_query, search_results=search_results
        )

    except Exception as e:
        app.logger.error(f"Error fetching playlist details: {e}")
        flash("An error occurred. Please try again.", "error")
        return redirect(url_for("user_playlists"))

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        flash("You need to log in to access your profile.", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]
    
    try:
        if request.method == "GET":
            response = requests.get(f"http://localhost:5000/api/users/{user_id}")
            if response.status_code != 200:
                flash("Failed to load profile information.", "error")
                return redirect(url_for("HomePage"))
            
            user = response.json()
            return render_template("profile.html", user=user)
        
        elif request.method == "POST":
            nickname = request.form.get("nickname")
            email = request.form.get("email")
            gender = request.form.get("gender")
            if not nickname or not email:
                flash("Nickname and email are required.", "error")
                return redirect(url_for("profile"))

            update_response = requests.put(
                f"http://localhost:5000/api/users/{user_id}",
                json={"nickname": nickname, "email": email, "gender": gender},
            )
            if update_response.status_code == 200:
                session["nickname"] = nickname
                flash("Profile updated successfully!", "success")
            else:
                flash("Failed to update profile. Try again.", "error")

            return redirect(url_for("profile"))

    except Exception as e:
        app.logger.error(f"Error fetching or updating profile: {e}")
        flash("An error occurred. Please try again later.", "error")
        return redirect(url_for("HomePage"))


@app.route("/profile/delete", methods=["POST"])
def delete_profile():
    if "user_id" not in session:
        flash("You need to log in to delete your profile.", "error")
        return redirect(url_for("login"))

    user_id = session["user_id"]

    try:
        delete_response = requests.delete(f"http://localhost:5000/api/users/{user_id}")
        if delete_response.status_code == 200:
            session.clear()
            flash("Account deleted successfully.", "success")
            return redirect(url_for("register"))
        else:
            flash("Failed to delete account. Try again.", "error")
            return redirect(url_for("profile"))

    except Exception as e:
        app.logger.error(f"Error deleting profile: {e}")
        flash("An error occurred. Please try again later.", "error")
        return redirect(url_for("profile"))


if __name__ == "__main__":
    db()
    app.run(host="0.0.0.0", port=5000, debug=True)
