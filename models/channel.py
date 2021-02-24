from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from models.channel_type import ChannelType

class Channel(db.Model):
    __tablename__ = "def_channel"

    iddef_channel = db.Column(db.Integer, primary_key=True)
    idop_sistemas = db.Column(db.Integer,  db.ForeignKey("def_channel_type.iddef_channel_type"), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    external_id = db.Column(db.String(100),nullable=False, default="")
    description = db.Column(db.String(250), nullable=False)
    iddef_channel_type = db.Column(db.Integer, db.ForeignKey("def_channel_type.iddef_channel_type"), nullable=False)
    url = db.Column(db.String(500),nullable=False, default="")
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class ChannelSchema(ma.Schema):
    iddef_channel = fields.Integer(dump_only=True)
    idop_sistemas = fields.Integer(required=True)
    external_id = fields.String(required=False)
    name = fields.String(required=True, validate=validate.Length(max=150))
    description = fields.String(required=True, validate=validate.Length(max=250))
    iddef_channel_type = fields.Integer(required=True)
    url = fields.String(required=True, validate=validate.Length(max=500))
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class ChannelRefSchema(ma.Schema):
    iddef_channel = fields.Integer(dump_only=True)
    idop_sistemas = fields.Integer(required=True)
    external_id = fields.String(required=False)
    url = fields.String(required=True, validate=validate.Length(max=500))
    name = fields.String(required=True, validate=validate.Length(max=150))
    description = fields.String(required=True, validate=validate.Length(max=250))
    iddef_channel_type = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")


class ChannelTableSchema(ma.Schema):
    iddef_channel = fields.Integer(dump_only=True)
    idop_sistemas = fields.Integer(required=True)
    external_id = fields.String(required=False)
    name = fields.String(required=True, validate=validate.Length(max=150))
    description = fields.String(required=True, validate=validate.Length(max=250))
    iddef_channel_type = fields.Integer(required=True)
    nombre_sistema = fields.String()
    name_channel_type = fields.String()
    url = fields.String(required=True, validate=validate.Length(max=500))
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
