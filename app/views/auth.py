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

from werkzeug.urls import url_parse

from app import BASE_DIR
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import current_user, logout_user, login_user

from app.forms import flash_errors
from app.forms.auth import RegistrationForm, LoginForm
from app.models import User
from app import db

blueprint = Blueprint('auth', __name__, template_folder=f'{BASE_DIR}/templates', url_prefix='/auth')


@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'GET':
        return render_template('auth/login.html', title='Sign in', form=form)

    if current_user.is_authenticated:
        return redirect(url_for('web.index'))

    if not form.validate_on_submit():
        flash_errors(form)
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=form.email.data).first()

    if user is None or not user.check_password(form.password.data):
        flash('Invalid email or password.', category='error')
        return redirect(url_for('auth.login'))

    login_user(user, remember=form.remember_me.data)

    next_page = request.args.get('next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('web.index')

    return redirect(next_page)


@blueprint.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('web.index'))


@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm(request.form)
    if request.method == 'GET':
        return render_template('auth/register.html', title='Register', form=form)

    if not form.validate_on_submit():
        flash_errors(form)
        return redirect(url_for('auth.register'))

    user = User()
    user.email = form.email.data
    user.set_password(form.password.data)
    user.generate_api_key()

    db.session.add(user)
    db.session.commit()

    return redirect(url_for('auth.login'))
