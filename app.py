import logging
import os
from flask import Flask
from flask_controllers import GameController, HealthCheck, Readiness
#from flask_helpers.fetch_config import fetch_config


log_format = "%(asctime)s %(levelname)s: %(message)s"
logging.basicConfig(level=logging.DEBUG, format=log_format)

#fetch_config()
#
game_version = "v0_1"
app = Flask(__name__)

try:
    app.config.from_pyfile(os.environ.get("COWBULL_CONFIG", "config/cowbull-prod.cfg"))
except FileNotFoundError:
    app.config["REDIS_HOST"] = "redis"
    app.config["REDIS_PORT"] = 6379
    app.config["REDIS_DB"] = 0

logging.debug("Configuration set to: {}".format(app.config))

# Add game view
game_view = GameController.as_view('Game')
app.add_url_rule('/{0}/game'.format(game_version), view_func=game_view, methods=["GET", "POST"])

# Add health view
health_view = HealthCheck.as_view('Health')
app.add_url_rule('/{0}/health'.format(game_version), view_func=health_view, methods=["GET"])

# Add readiness view
readiness_view = Readiness.as_view('ready')
app.add_url_rule('/{0}/ready'.format(game_version), view_func=readiness_view, methods=["GET"])

#
# If app.py has been run using Python, initiate a Flask object;
# otherwise, any caller (e.g. uWSGI or gunicorn) should initiate
# workers and routes.
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)