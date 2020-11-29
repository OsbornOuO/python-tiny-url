from http import HTTPStatus
from flask import Blueprint, request, jsonify, render_template, redirect, abort
# from flasgger import swag_from
from app.models.short_url import ShortURL
import json
from app.extensions import db

from app.errors import ToManyShortURL, NoSupportShortURLCharacter, NoSupportURL, InvalidInput


static_file = Blueprint('static_file', __name__)


@static_file.route('/<short_url>', methods=['GET'])
def encodeShortURL(short_url: str):
    if short_url == "favicon.ico":
        return "", 200
    print(short_url)
    result = ShortURL()
    result.init_by_decode(short_url)
    result = result.get_by_id()

    if result is None:
        return abort(404)

    return redirect(result.url), 301
