# -*- coding: utf-8 -*-
"""
    config
    ~~~~~~~~~~~~~~

    Setup app context and extensions

    :copyright: (c) 2019 by Software Clever, Palace Resorts CEDIS.
    :license: Private.
"""
from .flask import app, base, celery
from .extensions.db import db
from .extensions.api import api
from .extensions.ma import ma
from .routes import *
