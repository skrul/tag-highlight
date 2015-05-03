#!/usr/bin/env python
import flask
import flask_bootstrap
import tag_highlight

application = flask.Flask(__name__)
flask_bootstrap.Bootstrap(application)
application.register_blueprint(tag_highlight.app)
application.debug = True

if __name__ == '__main__':
    application.run()
