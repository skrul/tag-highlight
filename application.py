#!/usr/bin/env python
import flask
import flask_bootstrap
import tag_highlight

application = flask.Flask(__name__)
application.register_blueprint(tag_highlight.app)

if __name__ == '__main__':
    flask_bootstrap.Bootstrap(application)
    application.run(debug=True)
