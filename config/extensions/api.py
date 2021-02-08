# -*- coding: utf-8 -*-
"""
    app.extensions.api
    ~~~~~~~~~~~~~~

    Setup API Restful

    :copyright: (c) 2019 by Software Clever, Palace Resorts CEDIS.
    :license: Private.
"""
from config import app
from config import base
from flask_restful import Api

__all__ = ["api"]

api = Api(app, catch_all_404s=True, errors=base.werkzeug_errors())
