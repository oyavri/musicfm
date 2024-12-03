from flask import Flask
import logging
from database import db

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Log to console
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

app = Flask(__name__)

from resources.artists import artists_bp
app.register_blueprint(artists_bp, url_prefix="/")

@app.route("/")
def hello():
    return "Hello world!"

if __name__ == "__main__":
    # initialize singleton database instance
    db()
    # run flask app
    app.run(host="0.0.0.0", port=5000, debug=True)
