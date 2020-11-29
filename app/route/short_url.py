from http import HTTPStatus
from flask import Blueprint, request, jsonify, abort
# from flasgger import swag_from
from app.models.short_url import ShortURL
import json
from app.extensions import db

from app.errors import ToManyShortURL, NoSupportShortURLCharacter, NoSupportURL, InvalidInput, SameDomin


short_url_api = Blueprint('short_url_api', __name__)


@short_url_api.route('/', methods=['POST'])
def createShortURL():
    result = ShortURL()
    try:
        result.init_by_create(request.get_json())

        isValid = result.verify()
        result.create()
    except ToManyShortURL:
        return {
            "error": "short url is full",
        }, 500
    except NoSupportURL:
        return {
            "error": "url is not support",
        }, 400
    except InvalidInput:
        return {
            "error": "fail to bind json",
        }, 400
    except SameDomin:
        return {
            "error": "same domain",
        }, 400

    return result.toJSON(), 200


@short_url_api.route('/<string:short_url>', methods=['GET'])
def encodeShortURL(short_url: str):
    result = ShortURL()
    result.init_by_decode(short_url)
    result = result.get_by_id()

    return result.toJSON(), 301


@short_url_api.route('/<short_url>/preview', methods=['GET'])
def previewShortURL(short_url: str):
    result = ShortURL()
    result.init_by_decode(short_url)
    result = result.get_by_id()

    return result.toJSON(), 200
