# pste

[![License](https://img.shields.io/github/license/FoxDev/pste.svg)](https://www.gnu.org/licenses/gpl.txt)
[![Keybase PGP](https://img.shields.io/keybase/pgp/TheReverend403.svg)](https://keybase.io/thereverend403)

Just a simple file hosting application inspired by the likes of pomf.se and teknik.io.

Very early alpha, 100% definitely not ready whatsoever for production use. Not even for a laugh.

[Demo (latest dev)](https://dev.pste.pw)

# Quick Installation (dev)

First, install [Poetry](https://poetry.eustace.io/).

```sh
git clone https://github.com/FoxDev/pste
cd pste
poetry install # optional features: poetry install --extras "mysql postgresql gunicorn sentry"
cp config/default.toml config/settings.toml # Edit settings.toml
poetry shell

export FLASK_APP=pste
export FLASK_ENV=development

flask db upgrade
flask user create # Or use /auth/register

# Do not use this in production, use a WSGI server with pste:create_app() as your entrypoint.
flask run
```
