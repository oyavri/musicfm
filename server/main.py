from flask import Flask
import mysql.connector
import logging
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
connection = mysql.connector.connect(
            host="db",
            user="user",
            password="password",
            database="MUSICFM",
            port=3306
        )

@app.route("/")
def hello():
    return "Hello world!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
