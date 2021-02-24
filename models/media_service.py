from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate
from models.media import Media
from models.service import Service
from common.util import Util

class MediaService(db.Model):
    __tablename__ = "def_media_service"

    iddef_media_service = db.Column(db.Integer, primary_key=True)
    iddef_service = db.Column(db.Integer,db.ForeignKey("def_service.iddef_service"), nullable=False)
    service = db.relationship('Service', backref=db.backref('def_media_service', lazy="joined"))
    #service = db.relationship('Service', backref=db.backref('def_media_service', lazy="dynamic"))
    iddef_media = db.Column(db.Integer,db.ForeignKey("def_media.iddef_media"), nullable=False)
    media = db.relationship('Media', backref=db.backref('def_media_service', lazy="joined"))
    #media = db.relationship('Media', backref=db.backref('def_media_service', lazy="dynamic"))
    lang_code = db.Column(db.String(10),nullable=False)
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)


class MediaServiceSchema(ma.Schema):
    iddef_media_service = fields.Integer()
    iddef_service = fields.Integer(required=True)
    iddef_media = fields.Integer(required=True)
    lang_code = fields.String(validate=validate.Length(max=10))
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetMediaServiceSchema(ma.Schema):
    iddef_media_service = fields.Integer()
    iddef_service = fields.Integer()
    iddef_media = fields.Integer()
    lang_code = fields.String(validate=validate.Length(max=10))
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetListMediaServiceSchema(ma.Schema):
    iddef_media_service = fields.Integer()
    iddef_service = fields.Integer()
    service = ma.Pluck("ServiceSchema", 'currency_code')
    media =  ma.Nested("GetListMediaSchema",exclude=Util.get_default_excludes())
    lang_code = fields.String(validate=validate.Length(max=10))
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetMediaServiceAdminSchema(ma.Schema):
    iddef_media_service = fields.Integer()
    iddef_media = fields.Integer()
    iddef_service = fields.Integer()
    lang_code= fields.String(validate=validate.Length(max=10))
    name = fields.String(validate=validate.Length(max=100))
    description = fields.String(validate=validate.Length(max=150))
    url = fields.String(validate=validate.Length(max=100))
    selected = fields.Integer()
    tags = fields.Dict()
    etag = fields.String(required=True,validate=validate.Length(max=255))
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class PostMediaServiceSchema(ma.Schema):
    iddef_service = fields.Integer()
    lang_code= fields.String(validate=validate.Length(max=10))
    medias_id = fields.List(fields.Integer())
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
