from config import db, ma
from enum import Enum
from marshmallow import Schema, fields, validate
from datetime import datetime
from common.util import Util

class BookStatus(db.Model):
    __tablename__ = "book_status"

    on_process = 1
    cancel = 2
    on_hold = 3
    confirmed = 4
    changed = 5
    expired = 6
    interfaced = 7
    partial_interfaced = 8

    idbook_status = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)    

class BookStatusSchema(ma.Schema):
    idbook_status = fields.Integer()
    name = fields.String(required=True, validate=validate.Length(max=50))
    code = fields.String(required=True, validate=validate.Length(max=50))
    description = fields.String(required=True, validate=validate.Length(max=100))
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
