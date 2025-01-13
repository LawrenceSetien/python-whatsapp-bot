import logging
from flask import Flask, jsonify
from app.config import load_configurations, configure_logging
from app.views import webhook_blueprint


def create_app():
    app = Flask(__name__)

    # Load configurations and logging settings
    load_configurations(app)
    configure_logging()

    # Import and register blueprints, if any
    app.register_blueprint(webhook_blueprint)

    return app


app = create_app()


@app.route('/', methods=["GET", "POST"])
def first():
    return jsonify(status=200, message="Ok")


@app.route('/test', methods=["GET", "POST"])
def test():
    return jsonify({"message": "Success!"}), 200


if __name__ == "__main__":
    logging.info("Flask app started")
    app.run(host="0.0.0.0", port=8000)
