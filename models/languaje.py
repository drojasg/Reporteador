from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate

class Languaje(db.Model):

    __tablename__="def_language"

    iddef_language = db.Column(db.Integer,primary_key=True)
    lang_code = db.Column(db.String(10),nullable=False)
    description = db.Column(db.String(60),nullable=False)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)


class LanguajeSchema(ma.Schema):

    iddef_language = fields.Integer(dump_only=True)
    lang_code = fields.String(validate=validate.Length(max=10))
    description = fields.String(required=True,validate=validate.Length(max=10))
    estado = fields.Integer(load_only=True)
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetLanguajeSchema(ma.Schema):

    iddef_language = fields.Integer()
    lang_code = fields.String(validate=validate.Length(max=10))
    description = fields.String(required=True,validate=validate.Length(max=10))
    estado = fields.Integer(load_only=True)