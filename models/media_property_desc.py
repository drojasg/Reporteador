from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate
from models.media import Media, MediaSchema
from models.property_description import PropertyDescription, PropertyDescriptionSchema
from models.property import Property, PropertySchema
from models.media_property import MediaProperty,MediaPropertySchema
from common.util import Util
from sqlalchemy.orm import synonym
from common.base_audit import BaseAudit

class MediaPropertyDesc(db.Model, BaseAudit):
    __tablename__ = "def_media_property_desc"
    __table_args__ = {'extend_existing': True}

    iddef_media_property_desc = db.Column(db.Integer,primary_key=True)
    iddef_property = db.Column(db.Integer,db.ForeignKey("def_property"), nullable=False)
    propiedad = db.relationship('Property', backref=db.backref('def_property', lazy="joined"))
    iddef_description_type = db.Column(db.Integer,db.ForeignKey("def_property_description"), nullable=False)
    property_description = db.relationship('PropertyDescription', backref=db.backref('def_property_description', lazy="joined"))
    iddef_media = db.Column(db.Integer,db.ForeignKey("def_media"), nullable=False)
    media_data = db.relationship('Media', backref=db.backref('def_media', lazy="joined"))
    estado = db.Column(db.Integer,nullable=False)
    #estado = synonym("selected", map_column=True)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class MediaPropertyDescSchema(ma.Schema):
    iddef_media_property_desc = fields.Integer()
    iddef_property = fields.Integer(required=True)
    iddef_description_type = fields.Integer(required=True)
    iddef_media = fields.Integer(required=True)
    estado = fields.Integer()
    
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class MediaPropertyDescRefSchema(ma.Schema):
    iddef_media_property_desc = fields.Integer()
    iddef_property = fields.Integer(required=True)
    iddef_description_type = fields.Integer(required=True)
    iddef_media = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetMediaPropertyDescSchema(ma.Schema):
    iddef_media_property_desc = fields.Integer()
    propiedad = ma.Pluck("PropertySchema", 'iddef_property')
    tags = fields.Dict()
    name = fields.String(validate=validate.Length(max=100))
    etag = fields.String(required=True,validate=validate.Length(max=255))
    description = fields.String(validate=validate.Length(max=150))
    url = fields.String(validate=validate.Length(max=100))
    iddef_media = fields.Integer()
    media_data =  ma.Nested("GetListMediaSchema",exclude=Util.get_default_excludes())
    selected = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class PostMediaPropertyDescSchema(ma.Schema):
    iddef_property = fields.Integer()
    iddef_description_type = fields.Integer()
    medias_id = fields.List(fields.Integer())
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")