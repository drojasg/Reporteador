from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate
from models.amenity import Amenity
from models.property import Property
from common.util import Util

class PropertyAmenity(db.Model):
    __tablename__ = "def_property_amenity"

    iddef_property_amenity = db.Column(db.Integer, primary_key=True)
    iddef_amenity = db.Column(db.Integer,db.ForeignKey("def_amenity.iddef_amenity"), nullable=False)
    property_amenity = db.relationship('Amenity', backref=db.backref('def_property_amenity', lazy="dynamic"))
    iddef_property = db.Column(db.Integer,db.ForeignKey("def_property.iddef_property"), nullable=False)
    property = db.relationship('Property', backref=db.backref('def_property_amenity', lazy="dynamic"))
    is_priority = db.Column(db.Integer)
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)


class PropertyAmenitySchema(ma.Schema):
    iddef_property_amenity = fields.Integer()
    iddef_amenity = fields.Integer(required=True)
    iddef_property = fields.Integer(required=True)
    is_priority = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    property_amenity =  ma.Nested("AmenitySchema",exclude=Util.get_default_excludes())

class GetPropertyAmenitySchema(ma.Schema):
    iddef_property_amenity = fields.Integer()
    iddef_amenity = fields.Integer()
    iddef_property = fields.Integer()
    is_priority = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class PutPropertyAmenitySchema(ma.Schema):
    iddef_amenity = fields.Integer()
    property_amenity = ma.Pluck("GetListAmenitySchema", 'name')
    property = ma.Pluck("PropertySchema", 'property_code')
    is_priority = fields.Integer()
    estado = fields.Integer()

class SearchPropertyAmenitySchema(ma.Schema):
    iddef_property_amenity = fields.Integer(load_only=True)
    iddef_amenity = fields.Integer(load_only=True)
    iddef_property = fields.Integer(load_only=True)
    is_priority = fields.Integer()
    estado = fields.Integer(load_only=True)
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    property_amenity =  ma.Nested("GetListAmenitySchema",only=('name','html_icon',))
    property = ma.Pluck("PropertySchema", 'property_code')

class PropertyAmenityDescription(ma.Schema):
    iddef_amenity = fields.Integer()
    html_icon = fields.String()
    text = fields.String()
    attribute = fields.String(validate=validate.Length(max=100))
    is_priority = fields.Integer()
