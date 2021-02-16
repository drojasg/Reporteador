from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime

class ChannelType(db.Model):
    __tablename__ = "def_channel_type"

    iddef_channel_type = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class ChannelTypeSchema(ma.Schema):
    iddef_channel_type = fields.Integer()
    name = fields.String(required=True, validate=validate.Length(max=150))
    description = fields.String(required=True, validate=validate.Length(max=250))
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class ChannelTypeRefSchema(ma.Schema):
    iddef_channel_type = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(max=150))
    description = fields.String(required=True, validate=validate.Length(max=250))
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")