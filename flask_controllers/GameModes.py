import logging

from flask import request
from flask.views import MethodView
from flask_helpers.build_response import build_response

# Import the Game Controller
from Game.GameController import GameController


class GameModes(MethodView):
    def get(self):
        logging.debug("GameModes: GET: Initializing GameObject")
        game_object = GameController()
        logging.debug("GameModes: GET: GameObject initialized to {}".format(game_object.save()))

        logging.debug("GameModes: GET: Checking if textmode flag set")
        if request.args.get('textmode', None):
            logging.debug("GameModes: GET: Responding with list of names")
            response_data = game_object.game_mode_names
        else:
            logging.debug("GameModes: GET: Responding with JSON object")
            response_data = [{"mode": gt.mode,
                              "digits": gt.digits,
                              "digit-type": gt.digit_type,
                              "guesses": gt.guesses_allowed
                             } for gt in game_object.game_modes]

        logging.debug("GameModes: GET: Return {}".format(response_data))
        return build_response(
            html_status=200,
            response_data=response_data,
            response_mimetype="application/json"
        )
