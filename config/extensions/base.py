# -*- coding: utf-8 -*-
"""
    config.extensions.slave
    ~~~~~~~~~~~~~~

    BaseController contains methods that will be used in all resources

    :copyright: (c) 2019 by Software Clever, Palace Resorts CEDIS.
    :license: Private.
"""
from config import app
from .base_controller import BaseController

__all__ = ["base"]

base = BaseController(app)
