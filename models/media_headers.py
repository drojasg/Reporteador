from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate
from models.media import Media
from models.brand import Brand
from models.property import Property
from common.base_audit import BaseAudit

class MediaHeaders(db.Model, BaseAudit):
    __tablename__="def_media_headers"

    iddef_media_headers = db.Column(db.Integer, primary_key=True)
    iddef_media = db.Column(db.Integer, db.ForeignKey("def_media.iddef_media"), nullable=False)
    brand_code = db.Column(db.String, default = "",nullable=False)
    property_code = db.Column(db.String, default = "", nullable=False)
    all_lang = db.Column(db.Integer, default = 0, nullable=False)
    lang_code_list = db.Column(db.JSON, nullable=False, default ="{}")
    order = db.Column(db.Integer, default= 1,nullable=False)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class MediaHeadersSchema(ma.Schema):
    iddef_media_headers = fields.Integer()
    iddef_media = fields.Integer()
    brand_code = fields.String()
    property_code = fields.String()
    all_lang = fields.Integer()
    lang_code_list = fields.Dict() 
    order = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")


class MediaHeadersSchemaStatus(ma.Schema):
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class MediaHeadersGetSchema(ma.Schema):
    iddef_media_headers = fields.Integer()
    iddef_media = fields.Integer()
    property_code = fields.String()
    media_name = fields.String()
    order = fields.Integer()
    code = fields.String()
    brand_name = fields.String()
    property_name = fields.String()
    lang_code_list = fields.Dict()
    estado = fields.Integer()
    url = fields.String()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

