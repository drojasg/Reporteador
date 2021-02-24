from datetime import datetime
from config import db, ma
from models.filters import Filters
from models.property import Property
from marshmallow import Schema, fields, validate

class PropertyFilters(db.Model):
    __tablename__ = "def_property_filters"

    iddef_property_filters = db.Column(db.Integer, primary_key=True)
    iddef_property = db.Column(db.Integer,db.ForeignKey("def_property.iddef_property"), nullable=False)
    property = db.relationship('Property', backref=db.backref('def_property_filters', lazy="dynamic"))
    iddef_filter = db.Column(db.Integer,db.ForeignKey("def_filters.iddef_filters"), nullable=False)
    filters = db.relationship('Filters', backref=db.backref('def_property_filters', lazy="dynamic"))
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)


class PropertyFiltersSchema(ma.Schema):
    iddef_property_filters = fields.Integer(dump_only=True)
    iddef_property = fields.Integer(required=True)
    iddef_filter = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class getPropertyByFilters(ma.Schema):
    lang_code = fields.String(validate=validate.Length(max=10))
    market = fields.String(required=True)
    currency = fields.String(required=True)
    filters = fields.List(fields.Integer(),required=True)
    arrival_date = fields.Date()
    end_date = fields.Date()
    promo_code = fields.String(validate=validate.Length(max=6))

class GetPropertyFilterSchema(ma.Schema):
    iddef_property_lang = fields.Integer(dump_only=True)
    iddef_property = fields.Integer(load_only=True)
    property = ma.Pluck("PropertySchema", 'property_code')
    iddef_filter = fields.Integer()
    #filters = ma.Pluck("FiltersSchema", 'name')
    filters = fields.String(dump_only=True, default="")
    property_code = fields.String(required=True, load_only=True)
    brand_code = fields.String(required=True, load_only=True)
    lang_code = fields.String(load_only=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")