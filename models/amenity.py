from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate
from models.amenity_type import AmenityType, AmenityTypeSchema
from models.amenity_group import AmenityGroup, AmenityGroupSchema, getNameGroupSchema
from models.text_lang import PostPutTextLangSchema as txt_schema
from common.util import Util

class Amenity(db.Model):
    __tablename__ = "def_amenity"

    iddef_amenity = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    html_icon = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)
    iddef_amenity_group = db.Column(db.Integer,db.ForeignKey("def_amenity_group.iddef_amenity_group"), nullable=False)
    amenity_group = db.relationship('AmenityGroup', backref=db.backref('def_amenity_group', lazy='joined'))
    iddef_amenity_type = db.Column(db.Integer,db.ForeignKey("def_amenity_type.iddef_amenity_type"), nullable=False)
    amenity_type = db.relationship('AmenityType', backref=db.backref('def_amenity_type', lazy='joined'))

class AmenitySchema(ma.Schema):
    iddef_amenity = fields.Integer()
    name = fields.String(
        required=True, validate=validate.Length(max=45))
    description = fields.String(
        required=True, validate=validate.Length(max=200))
    html_icon = fields.String(
        required=True, validate=validate.Length(max=50))
    #is_priority = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(
        required=False, validate=validate.Length(max=45),  default="")
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    iddef_amenity_group = fields.Integer(required=True)
    iddef_amenity_type = fields.Integer(required=True)

class AmenityPostPutSchema(ma.Schema):
    iddef_amenity = fields.Integer()
    name = fields.String(
        required=True, validate=validate.Length(max=45))
    description = fields.String(
        required=True, validate=validate.Length(max=200))
    html_icon = fields.String(
        required=True, validate=validate.Length(max=50))
    #is_priority = fields.Integer()
    estado = fields.Integer()
    info_amenity_by_lang = fields.List(fields.Nested(txt_schema),dump_only=False)
    usuario_creacion = fields.String(
        required=False, validate=validate.Length(max=45),  default="")
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    iddef_amenity_group = fields.Integer(required=True)
    iddef_amenity_type = fields.Integer(required=True)


class GetAmenitySchema(ma.Schema):
    iddef_amenity = fields.Integer()
    name = fields.String(validate=validate.Length(max=45))
    description = fields.String(validate=validate.Length(max=200))
    html_icon = fields.String(validate=validate.Length(max=50))
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45),  default="")
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45),  default="")
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    iddef_amenity_group = fields.Integer()
    iddef_amenity_type = fields.Integer()

class GetListAmenitySchema(ma.Schema):
    iddef_amenity = fields.Integer()
    name = fields.String(validate=validate.Length(max=45))
    description = fields.String(validate=validate.Length(max=200))
    html_icon = fields.String(validate=validate.Length(max=50))
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45), default="")
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    #amenity_group = ma.Pluck("AmenityGroupSchema", 'name')
    #amenity_type = ma.Pluck("AmenityTypeSchema", 'descripcion')
    amenity_group = ma.Nested("AmenityGroupSchema", exclude=Util.get_default_excludes())
    amenity_type = ma.Nested("AmenityTypeSchema",exclude=Util.get_default_excludes())


class GetIdAmenitySchema(ma.Schema):
    nombre = fields.String(validate=validate.Length(max=45))
    estado = fields.Integer()
    is_priority = fields.Integer()

class IdAmenitySchema(ma.Schema):
    iddef_amenity = fields.Integer()

class RoomAmenity(ma.Schema):
    iddef_amenity = fields.Integer()
    html_icon = fields.String()
    text = fields.String()
    is_priority = fields.Integer()
    attribute = fields.String(validate=validate.Length(max=100))

class publicAmenities(ma.Schema):
    iddef_amenity = fields.Integer()
    name = fields.String()
    description = fields.String()
    is_priority = fields.Integer()
    html_icon = fields.String()