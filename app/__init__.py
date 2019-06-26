#  This file is part of pste.
#
#  pste is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  pste is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with pste.  If not, see <https://www.gnu.org/licenses/>.

import os

from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

migrate = Migrate()
login = LoginManager()
db = SQLAlchemy()
csrf = CSRFProtect()


def create_app():
    app = Flask('pste', static_folder=f'{BASE_DIR}/static', template_folder=f'{BASE_DIR}/templates')
    app.config.from_object('app.settings')

    register_extensions(app)

    from app.views import register_blueprints
    register_blueprints(app)

    from app import commands
    commands.init_app(app)

    return app


def register_extensions(app):
    if app.config['SENTRY_DSN']:
        try:
            import sentry_sdk
            from sentry_sdk.integrations.flask import FlaskIntegration

            sentry_sdk.init(dsn=app.config['SENTRY_DSN'], integrations=[FlaskIntegration()])
        except ImportError:
            app.logger.warn('SENTRY_DSN is set but the sentry-sdk library is not available. Sentry will not be used.')

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login.init_app(app)
    login.login_view = 'auth.login'
