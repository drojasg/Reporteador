from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from common.util import Util

class AuthItem(db.Model):
    __tablename__ = "auth_item"

    name = db.Column(db.String(64), primary_key=True)
    type = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(250), nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class AuthItemSchema(ma.Schema):
    name = fields.String(validate=validate.Length(max=64))
    type = fields.Integer()
    description = fields.String(required=False, validate=validate.Length(max=250))    
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")