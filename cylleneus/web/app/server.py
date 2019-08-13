import flask

from .settings import *

app = flask.Flask('app')

from . import views

def run():
    """Run the Flask server."""

    app.run(
        host=HOST_ADDR,
        port=HOST_PORT,
        debug=True,
        threaded=not PROCESSES > 1,
        processes=PROCESSES
    )
