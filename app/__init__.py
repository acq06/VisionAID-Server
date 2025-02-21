from flask import Flask, request, jsonify
from flask_cors import CORS
from app.utils import model
import base64
import os


def create_app():
    """
    :return app: Flask app
    """
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@localhost/oculi"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["MAX_CONTENT_LENGTH"] = (
        16 * 1024 * 1024
    )  # Limit to 16 MB, adjust as needed
    app.json.sort_keys = False
    app.secret_key = "Oculi"

    CORS(app)

    @app.route("/")
    def home():
        return "Vision AID"

    @app.post("/api/read")
    def read():
        data = request.get_json()

        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        image = data.get("image")
        print(image)
        text = str(model.read_image(image))
        print(f"Text: {text}")
        return text

    return app


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string
