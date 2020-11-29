# coding:utf-8
import os

from flask import Flask, request, current_app, jsonify, g
from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis
from flask_migrate import Migrate
from .extensions import db, redis_store, migrate
from werkzeug.exceptions import HTTPException
import traceback
import sys
import uuid
import json
import logging
from logging.config import dictConfig


def create_app():
    app = Flask(__name__, static_url_path='')

    app.config.from_pyfile('../deployment/configs/app.cfg', silent=True)

    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
            'formatter': 'default'
        }},
        'root': {
            'level': 'DEBUG',
            'handlers': ['wsgi']
        }
    })

    register_extensions(app)
    register_errorhandlers(app)
    register_blueprints(app)
    register_access_log(app)

    return app


def register_extensions(app):
    db.init_app(app)
    redis_store.init_app(app)
    migrate.init_app(app, db)


def register_errorhandlers(app):
    @app.errorhandler(404)
    def page_not_found(e):
        # note that we set the 404 status explicitly
        return app.send_static_file('404.html')

    @app.errorhandler(Exception)
    def errors(e):
        message = getattr(e, 'description', None) or getattr(
            e, 'msg', None) or str(e)

        error = {
            'code': str(getattr(e, 'code', 500)),
            'name': str(getattr(e, 'name', '')),
            'message': message
        }

        error['trace'] = traceback.format_exception(*sys.exc_info())
        print(''.join(error['trace']))

        code = error['code'] if isinstance(e, HTTPException) else 500

        return jsonify(error), int(code)


def register_blueprints(app):
    from app.route.short_url import short_url_api
    app.register_blueprint(short_url_api, url_prefix='/api/v1/shorten')

    from app.route.static_file import static_file
    app.register_blueprint(static_file, url_prefix='/')

    @app.route('/')
    def index():
        return app.send_static_file('index.html')


def register_access_log(app):
    def save_request(request):
        req_data = {}
        req_data['endpoint'] = request.endpoint
        req_data['method'] = request.method
        req_data['cookies'] = request.cookies
        req_data['data'] = request.data
        req_data['headers'] = dict(request.headers)
        req_data['headers'].pop('Cookie', None)
        req_data['args'] = request.args
        req_data['form'] = request.form
        req_data['remote_addr'] = request.remote_addr
        files = []
        for name, fs in request.files.items():
            dst = tempfile.NamedTemporaryFile()
            fs.save(dst)
            dst.flush()
            filesize = os.stat(dst.name).st_size
            dst.close()
            files.append({'name': name, 'filename': fs.filename, 'filesize': filesize,
                          'mimetype': fs.mimetype, 'mimetype_params': fs.mimetype_params})
        req_data['files'] = files
        return req_data

    def save_response(resp):
        resp_data = {}
        resp_data['status_code'] = resp.status_code
        resp_data['status'] = resp.status
        resp_data['headers'] = dict(resp.headers)
        resp_data['data'] = resp.response
        return resp_data

    @app.after_request
    def after_request(resp):
        req_data = save_request(request)
        resp_data = save_response(resp)
        params = request.args if request.method == 'GET' else request.get_json()
        app.logger.info(
            '{} | {} | {}'.format(request.method, request.path, params))

        resp.headers.add('Access-Control-Allow-Origin', '*')
        resp.headers.add('Access-Control-Allow-Headers',
                         'Content-Type, X-Token')
        resp.headers.add('Access-Control-Allow-Methods',
                         'GET, POST, PUT, DELETE')
        return resp
