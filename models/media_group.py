from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate
from models.property import Property, PropertySchema


class MediaGroup(db.Model):
    __tablename__ = "def_media_group"
    __table_args__ = {'extend_existing': True}

    iddef_media_group = db.Column(db.Integer, primary_key=True)
    iddef_property = db.Column(db.Integer,db.ForeignKey("def_property"), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)


class MediaGroupSchema(ma.Schema):
    iddef_media_group = fields.Integer()
    iddef_media_property_desc = ma.Pluck("PropertySchema", 'iddef_property')
    description = fields.String(required=True, validate=validate.Length(max=100))
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetMediaGroupSchema(ma.Schema):
    iddef_media_group = fields.Integer()
    description = fields.String(validate=validate.Length(max=100))
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class UpdateMediaGroupStatusGallery(ma.Schema):
    estado = fields.Integer()
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
