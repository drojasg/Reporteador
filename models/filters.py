from datetime import datetime
from config import db, ma
from models.text_lang import PostPutTextLangSchema as txt_schema
from marshmallow import Schema, fields, validate

class Filters(db.Model):
    __tablename__="def_filters"
    __table_args__ = {'extend_existing': True} 

    iddef_filters = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(45),nullable=False)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)


class FiltersSchema(ma.Schema):
    iddef_filters = fields.Integer(dump_only=True)
    name = fields.String(required=False, validate=validate.Length(max=45))
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class FiltersPostPutSchema(ma.Schema):
    iddef_filters = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(max=45))
    info_filters_by_lang = fields.List(fields.Nested(txt_schema),dump_only=False)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")