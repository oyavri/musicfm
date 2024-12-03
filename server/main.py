from flask import Flask
import logging
from database import db
import time

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Log to console
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

app = Flask(__name__)
db_config = {
            "host":"db",
            "user":"user",
            "password":"password",
            "database":"MUSICFM",
            "port":3306       
}

@app.route("/")
def hello():
    return "Hello world!"

if __name__ == "__main__":
    # initialize singleton database instance
    db(db_config)
    # run flask app
    app.run(host="0.0.0.0", port=5000, debug=True)
