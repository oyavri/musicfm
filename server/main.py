from flask import Flask
import logging
from database import db

app = Flask(__name__)
app.logger.setLevel(logging.ERROR)
app.url_map.strict_slashes = False

from resources.artists import artists_bp
app.register_blueprint(artists_bp, url_prefix="/")

from resources.albums import albums_bp
artists_bp.register_blueprint(albums_bp)

@app.route("/")
def hello():
    return "Hello world!"

if __name__ == "__main__":
    # initialize the singleton database instance
    db()
    # run flask app
    app.run(host="0.0.0.0", port=5000, debug=True)
