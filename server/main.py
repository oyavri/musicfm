from flask import Flask
import logging
from database import db

from resources.artists import artists_bp
from resources.albums import albums_bp
from resources.tracks import tracks_bp
from resources.users import users_bp
from resources.likes import likes_bp

app = Flask(__name__)
app.logger.setLevel(logging.ERROR)
app.url_map.strict_slashes = False
app.json.ensure_ascii = False # due to turkish characters

artists_bp.register_blueprint(tracks_bp)
artists_bp.register_blueprint(albums_bp)
users_bp.register_blueprint(likes_bp)
app.register_blueprint(artists_bp, url_prefix="/")
app.register_blueprint(users_bp, url_prefix="/")

@app.route("/")
def hello():
    return "Hello world!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
