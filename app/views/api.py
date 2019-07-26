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

import hashlib
import os
from pathlib import Path

import magic
from flask import Blueprint, jsonify, request, url_for
from flask_login import login_required, current_user

from app import db, csrf
from app.forms.api import UploadForm
from app.models import File
from app import utils

blueprint = Blueprint('api', __name__, url_prefix='/api')


@blueprint.route('/upload', methods=['POST'])
@login_required
@csrf.exempt
def upload():
    form = UploadForm(request.files)
    if not form.validate_on_submit():
        return jsonify({'errors': form.errors})

    fd = form.file.data

    fd.seek(0, os.SEEK_END)
    file_size = fd.tell()
    fd.seek(0)

    if file_size + current_user.get_disk_usage() > current_user.get_quota() and not current_user.is_admin:
        return jsonify({'error': f'Storage limit reached ({current_user.get_quota(humanize=True)})'})

    file_contents = fd.read()
    fd.seek(0)

    file_hash = hashlib.sha256(file_contents).hexdigest()
    file_mimetype = magic.from_buffer(file_contents, mime=True)

    extension = Path(fd.filename).suffix
    slug = utils.generate_slug()
    if extension:
        slug = slug + extension

    existing_file = File.query.filter_by(user=current_user, file_hash=file_hash).first()
    if existing_file:
        existing_file.name = fd.filename
        db.session.commit()
        return jsonify({'url': url_for('web.file', slug=existing_file.slug, _external=True)})

    file = File(user=current_user)
    file.name = fd.filename
    file.size = file_size
    file.file_hash = file_hash
    file.client_mimetype = fd.mimetype
    file.server_mimetype = file_mimetype
    file.slug = slug

    fd.save(file.path())

    db.session.add(file)
    db.session.commit()

    return jsonify({'url': url_for('web.file', slug=file.slug, _external=True)})
