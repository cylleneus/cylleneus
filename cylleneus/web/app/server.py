import flask

from .settings import *

app = flask.Flask('app')


def run():
    """Run the Flask server."""

    app.run(
        host=HOST_ADDR,
        port=HOST_PORT,
        debug=DEBUG,
        threaded=not PROCESSES > 1,
        processes=PROCESSES
    )
