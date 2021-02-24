from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate
from models.media import Media
from models.property import Property
from common.util import Util
from models.property import Property,PropertySchema

class MediaProperty(db.Model):
    __tablename__ = "def_media_property"

    iddef_media_property = db.Column(db.Integer, primary_key=True)
    iddef_property = db.Column(db.Integer,db.ForeignKey("def_property.iddef_property"), nullable=False)
    property = db.relationship('Property', backref=db.backref('def_media_property', lazy="joined"))
    iddef_media = db.Column(db.Integer,db.ForeignKey("def_media.iddef_media"), nullable=False)
    media = db.relationship('Media', backref=db.backref('def_media_property', lazy="joined"))
    order = db.Column(db.Integer,nullable=False)
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class MediaPropertySchema(ma.Schema):
    iddef_media_property = fields.Integer()
    iddef_property = fields.Integer(required=True)
    iddef_media = fields.Integer(required=True)
    order = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetMediaPropertySchema(ma.Schema):
    iddef_media_property = fields.Integer()
    iddef_property = fields.Integer()
    iddef_media = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetListMediaPropertySchema(ma.Schema):
    iddef_media_property = fields.Integer()
    iddef_property = fields.Integer()
    property = ma.Pluck("PropertySchema", 'property_code')
    media =  ma.Nested("GetListMediaSchema",exclude=Util.get_default_excludes())
    order = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetMediaPropertyAdminSchema(ma.Schema):
    iddef_media_property = fields.Integer()
    #iddef_property =  ma.Pluck("PropertySchema", 'iddef_property')
    iddef_media = fields.Integer()
    name = fields.String(validate=validate.Length(max=100))
    description = fields.String(validate=validate.Length(max=150))
    url = fields.String(validate=validate.Length(max=100))
    selected = fields.Integer()
    tags = fields.Dict()
    etag = fields.String(required=True,validate=validate.Length(max=255))
    order = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class PostMediaPropertySchema(ma.Schema):
    iddef_property = fields.Integer()
    order = fields.Integer()
    medias_id = fields.List(fields.Dict())
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")


class UpdateOrderSchema(ma.Schema):
    iddef_media_property = fields.Integer()
    order = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")