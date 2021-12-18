from flask import Flask, render_template

import os
from . import models, auth, report, graph


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///'+os.path.join(app.instance_path, 'reports.db'))
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

        # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    models.init_app(app)
    if not app.config.get("TESTING"):
        models.load_data()
        print("loaded")
    app.register_blueprint(auth.bp)
    app.register_blueprint(report.bp)
    app.register_blueprint(graph.bp)
    app.add_url_rule('/', endpoint='index')

    return app

