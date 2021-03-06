from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate
from models.segment import Segment
from models.property_type import PropertyType
from models.brand import Brand
from models.area_unit import AreaUnit, AreaUnitSchema
from models.property_category import PropertyCategory
from models.zones import Zones
from models.time_zone import TimeZone, TimeZoneSchema
from models.media import publicGetListMedia
from models.amenity import publicAmenities
from .contact import Contact, ContactSchema
from .policy import Policy, PolicySchema
from common.util import Util

contact_properties = db.Table('def_contact_property',
    db.Column('iddef_property', db.Integer, db.ForeignKey('def_property.iddef_property'), primary_key=True),
    db.Column('iddef_contact', db.Integer, db.ForeignKey('def_contact.iddef_contact'), primary_key=True),
    db.Column('iddef_market', db.Integer, nullable=False, default=0)
)

# policy_properties = db.Table('def_policy_property',
#     db.Column('iddef_property', db.Integer, db.ForeignKey('def_property.iddef_property'), primary_key=True),
#     db.Column('iddef_policy', db.Integer, db.ForeignKey('def_policy.iddef_policy'), primary_key=True)
# )

class Property(db.Model):
    __tablename__ = "def_property"

    iddef_property = db.Column(db.Integer, primary_key=True)
    short_name = db.Column(db.String(45), nullable=False)
    trade_name = db.Column(db.String(45), nullable=False)
    property_code = db.Column(db.String(6), nullable=False)
    web_address = db.Column(db.String(300), nullable=False)
    #currency_code = db.Column(db.String(10), nullable=False)
    #time_zone = db.Column(db.String(50), nullable=False)
    icon_logo_name = db.Column(db.String(50), nullable=False)
    #push_property = db.Column(db.Integer, nullable=False, default=0)
    iddef_brand = db.Column(db.Integer, db.ForeignKey("def_brand.iddef_brand"), nullable=False)
    brand = db.relationship('Brand', backref=db.backref('def_property', lazy=True))
    #iddef_area_unit = db.Column(db.Integer, db.ForeignKey("def_area_unit.iddef_area_unit"), nullable=False)
    #area_unit_p = db.relationship('AreaUnit', backref=db.backref('def_area_unit', lazy=True))
    iddef_property_type = db.Column(db.Integer, db.ForeignKey("def_property_type.iddef_property_type"), nullable=False)
    property_type = db.relationship('PropertyType', backref=db.backref('def_property', lazy=True))
    #iddef_segment = db.Column(db.Integer, db.ForeignKey("def_segment.iddef_segment"), nullable=True)
    #segment = db.relationship('Segment', backref=db.backref('def_property', lazy=True))
    #iddef_property_category = db.Column(db.Integer, db.ForeignKey("def_property_category.iddef_property_category"), nullable=True)
    #property_category = db.relationship('PropertyCategory', backref=db.backref('def_property', lazy=True))
    #iddef_zone = db.Column(db.Integer, db.ForeignKey("def_zones.iddef_zones"), nullable=True)
    #zone = db.relationship('Zones', backref=db.backref('def_property', lazy=True))
    iddef_time_zone = db.Column(db.Integer, db.ForeignKey("def_time_zone.iddef_time_zone"), nullable=False)
    property_time_zone = db.relationship('TimeZone', backref=db.backref('def_property', lazy=True))
    sender = db.Column(db.String(150), default="")
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)
    contacts = db.relationship('Contact', secondary=contact_properties, lazy='subquery', backref=db.backref('properties', lazy=True))
    #policies = db.relationship('Policy', secondary=policy_properties, lazy='dynamic', backref=db.backref('properties', lazy=True))
    

class PropertyBookSchema(ma.Schema): #No se ocupa
    iddef_property = fields.Integer()
    short_name = fields.String(required=True, validate=validate.Length(max=45))
    trade_name = fields.String(required=True, validate=validate.Length(max=45))
    property_code = fields.String(required=True, validate=validate.Length(max=6))
    #web_address = fields.String(required=True, validate=validate.Length(max=300))
    #currency_code = fields.String(required=True, validate=validate.Length(max=10))
    #time_zone = fields.String(required=True, validate=validate.Length(max=50))
    #push_property = fields.Integer(required=True)
    #iddef_brand = fields.Integer(required=True)
    brand = ma.Pluck("BrandSchema", 'name')
    #iddef_area_unit = fields.Integer(required=True)
    #iddef_property_type = fields.Integer(required=True)
    #iddef_property_category = fields.Integer(required=True)
    #iddef_segment = fields.Integer(required=True)
    #iddef_zone = fields.Integer(required=True)
    image_url = fields.List(fields.Nested(publicGetListMedia),dump_only=True)

class PropertySchema(ma.Schema):
    iddef_property = fields.Integer()
    short_name = fields.String(required=True, validate=validate.Length(max=45))
    trade_name = fields.String(required=True, validate=validate.Length(max=45))
    property_code = fields.String(required=True, validate=validate.Length(max=6))
    web_address = fields.String(required=True, validate=validate.Length(max=300))
    #currency_code = fields.String(required=True, validate=validate.Length(max=10))
    #time_zone = fields.String(required=True, validate=validate.Length(max=50))
    icon_logo_name = fields.String(required=True, validate=validate.Length(max=50))
    #push_property = fields.Integer(required=True)
    iddef_brand = fields.Integer(required=True)
    brand = ma.Pluck("BrandSchema", 'name')
    #iddef_area_unit = fields.Integer(required=True)
    iddef_property_type = fields.Integer(required=True)
    #iddef_property_category = fields.Integer(required=True)
    #iddef_segment = fields.Integer(required=True)
    #iddef_zone = fields.Integer(required=True)
    property_lang = fields.List(fields.Integer(),required=True)
    filters = fields.List(fields.Integer(), required=True)
    image_url = fields.String(dump_only=True)
    iddef_time_zone = fields.Integer(required=True)
    property_time_zone = fields.Nested(TimeZoneSchema(only=("name", "code"))) #ma.Pluck("TimeZoneSchema", 'name')
    sender = fields.String(validate=validate.Length(max=150))
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetPropertySchema(ma.Schema): #No se ocupa
    iddef_property = fields.Integer()
    short_name = fields.String(validate=validate.Length(max=45))
    trade_name = fields.String(validate=validate.Length(max=45))
    property_code = fields.String(validate=validate.Length(max=6))
    web_address = fields.String(validate=validate.Length(max=300))
    #currency_code = fields.String(validate=validate.Length(max=10))
    #time_zone = fields.String(validate=validate.Length(max=50))
    #push_property = fields.Integer(required=True)
    iddef_brand = fields.Integer()
    #iddef_area_unit = fields.Integer()
    iddef_property_type = fields.Integer()
    #iddef_segment = fields.Integer()
    #iddef_property_category = fields.Integer()
    #iddef_zone = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45),default="")
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45), default="")
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetListFilterPropertySchema(ma.Schema):
    iddef_property = fields.Integer()
    short_name = fields.String(validate=validate.Length(max=45))
    trade_name = fields.String(validate=validate.Length(max=45))
    property_code = fields.String(validate=validate.Length(max=6))
    web_address = fields.String(validate=validate.Length(max=300))
    #currency_code = fields.String(validate=validate.Length(max=10))
    #time_zone = fields.String(validate=validate.Length(max=50))
    #push_property = fields.Integer()
    iddef_brand = fields.Integer()
    brand = ma.Pluck("BrandSchema", 'name')
    #iddef_area_unit = fields.Integer()
    #area_unit_p = fields.Nested(AreaUnitSchema, only=('description','unit_code',))
    #AreaUnit = ma.Pluck("AreaUnitSchema", 'description')
    iddef_property_type = fields.Integer()
    property_type = ma.Pluck("PropertyTypeSchema", 'description')
    #iddef_segment = fields.Integer()
    #segment = ma.Pluck("SegmentSchema", 'description')
    #iddef_property_category = fields.Integer()
    #property_category = ma.Pluck("PropertyCategorySchema", 'name')
    #iddef_zone = fields.Integer()
    #zone = ma.Pluck("ZonesSchema", 'name')
    iddef_time_zone = fields.Integer(required=True)
    property_time_zone = fields.Nested(TimeZoneSchema(only=("name", "code")))
    sender = fields.String(validate=validate.Length(max=150))
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45), default="")
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45), default="")
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetListPropertySchema(ma.Schema):
    iddef_property = fields.Integer()
    short_name = fields.String(validate=validate.Length(max=45))
    trade_name = fields.String(validate=validate.Length(max=45))
    property_code = fields.String(validate=validate.Length(max=6))
    web_address = fields.String(validate=validate.Length(max=300))
    #currency_code = fields.String(validate=validate.Length(max=10))
    #time_zone = fields.String(validate=validate.Length(max=50))
    #push_property = fields.Integer(required=True)
    brand = ma.Pluck("BrandSchema", 'name')
    #iddef_area_unit = fields.Integer()
    property_type = ma.Pluck("PropertyTypeSchema", 'description')
    #segment = ma.Pluck("SegmentSchema", 'description')
    #property_category = ma.Pluck("PropertyCategorySchema", 'name')
    #zone = ma.Pluck("ZonesSchema", 'name')
    iddef_time_zone = fields.Integer(required=True)
    property_time_zone = fields.Nested(TimeZoneSchema(only=("name", "code")))
    sender = fields.String(validate=validate.Length(max=150))
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45), default="")
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45), default="")
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetPropertyContactsSchema(ma.Schema):
    iddef_property = fields.Integer()
    short_name = fields.String(required=True, validate=validate.Length(max=45))
    trade_name = fields.String(required=True, validate=validate.Length(max=45))
    property_code = fields.String(required=True, validate=validate.Length(max=6))
    web_address = fields.String(required=True, validate=validate.Length(max=300))
    #currency_code = fields.String(required=True, validate=validate.Length(max=10))
    #time_zone = fields.String(required=True, validate=validate.Length(max=50))
    iddef_brand = fields.Integer(required=True)
    #iddef_area_unit = fields.Integer(required=True)
    iddef_property_type = fields.Integer(required=True)
    #iddef_property_category = fields.Integer(required=True)
    #iddef_segment = fields.Integer(required=True)
    #iddef_zone = fields.Integer(required=True)
    iddef_time_zone = fields.Integer(required=True)
    sender = fields.String(validate=validate.Length(max=150))
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45),default="")
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45), default="")
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    contacts = fields.Nested(ContactSchema, many=True, exclude=Util.get_default_excludes())

class GetPropertyPolicySchema(ma.Schema): #No se ocupa
    iddef_property = fields.Integer()
    short_name = fields.String(required=True, validate=validate.Length(max=45))
    trade_name = fields.String(required=True, validate=validate.Length(max=45))
    property_code = fields.String(required=True, validate=validate.Length(max=6))
    web_address = fields.String(required=True, validate=validate.Length(max=300))
    #currency_code = fields.String(required=True, validate=validate.Length(max=10))
    #time_zone = fields.String(required=True, validate=validate.Length(max=50))
    iddef_brand = fields.Integer(required=True)
    #iddef_area_unit = fields.Integer(required=True)
    iddef_property_type = fields.Integer(required=True)
    #iddef_property_category = fields.Integer(required=True)
    #iddef_segment = fields.Integer(required=True)
    #iddef_zone = fields.Integer(required=True)
    iddef_time_zone = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45), default="")
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45), default="")
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    #policies = fields.Nested(PolicySchema, many=True, exclude=Util.get_default_excludes())

class GetSearchHotelsSchema(ma.Schema): #No se ocupa
    arrival_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    promo_code = fields.String(required=True, validate=validate.Length(max=6))
    rooms = fields.Nested("GetDataRoomsSchema", many=True)

class GetSearchRoomsSchema(ma.Schema):
    lang_code = fields.String(validate=validate.Length(max=10))
    currency = fields.String(required=True, validate=validate.Length(max=10))
    market = fields.String(required=True, validate=validate.Length(max=15))
    hotel_code = fields.String(required=True, validate=validate.Length(max=6))
    arrival_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    promo_code = fields.String(required=True, validate=validate.Length(max=6))
    rooms = fields.List(fields.Dict(fields.String(),fields.Integer()),required=True)
    #rooms = fields.List(fields.Nested("GetDataRoomsSchema"),required=True, many=True)
    #rooms = fields.Nested("GetDataRoomsSchema", many=True)

class GetDataRoomsSchema(ma.Schema): #No se ocupa
    adults = fields.Integer()
    teens = fields.Integer()
    kids = fields.Integer()
    infants = fields.Integer()

class GetDataRatePlanSchema(ma.Schema):
    idop_rate_plan = fields.Integer()
    plan_code = fields.String(validate=validate.Length(max=45))
    plan_name = fields.String(validate=validate.Length(max=350))
    nights = fields.Integer()
    total = fields.Float()
    total_crossout = fields.Float()
    price_per_day = fields.List(fields.Nested("GetDataPricePerDaySchema"), many=True)
    total_percent_discount = fields.Integer()
    night_price = fields.Float()

class GetDataPricePerDaySchema(ma.Schema):
    nights = fields.Integer()
    amount = fields.Float()
    amount_crossout = fields.Float()
    percent_discount = fields.Integer()
    efective_date = fields.Date()

class PublicProperty(ma.Schema):
    date_start = fields.Date(load_only=True)
    date_end = fields.Date(load_only=True)
    #property_code = fields.String(load_only=True)
    market = fields.String(required=True,load_only=True)
    lang_code = fields.String(required=True,load_only=True)
    filters = fields.List(fields.Integer())
    property_code = fields.String(required=True)
    brand_code = fields.String(required=True)
    property_icon = fields.String(dump_only=True)
    #iddef_segment = fields.Integer(dump_only=True)
    trade_name = fields.String(dump_only=True)
    short_name = fields.String(dump_only=True)
    #time_zone = fields.String(dump_only=True)
    web_address = fields.String(dump_only=True)
    iddef_property = fields.Integer(dump_only=True)
    description = fields.String(dump_only=True)
    iddef_time_zone = fields.Integer(dump_only=True)
    sender = fields.String(dump_only=True)
    estado = fields.Integer(dump_only=True)
    media = fields.List(fields.Nested(publicGetListMedia),dump_only=True)
    amenity = fields.List(fields.Nested(publicAmenities),dump_only=True)
    service = fields.List(fields.Dict(),dump_only=True)
    avail_msg = fields.String(dump_only=True)
    terms_and_conditions = fields.String(dump_only=True)

class PublicPropertyInfo(ma.Schema):
    property_code = fields.String(required=True)
    brand_code = fields.String(required=True)
    trade_name = fields.String(dump_only=True)
    short_name = fields.String(dump_only=True)
    icon_logo_name = fields.String(dump_only=True)
    media = fields.List(fields.Nested(publicGetListMedia),dump_only=True)

class PublicPropertyAmenityMedia(ma.Schema):
    lang_code = fields.String(required=True,load_only=True)
    property_code = fields.String(required=True)
    media = fields.List(fields.Nested(publicGetListMedia),dump_only=True)
    amenity = fields.List(fields.Nested(publicAmenities),dump_only=True)

class GetSearchEmailsSchema(ma.Schema):
    email = fields.String()

class GetHoldPublicSchema(ma.Schema):
    property_code = fields.String(required=True,load_only=True)
    from_date = fields.Date(required=True,load_only=True)
    to_date = fields.Date(required=True,load_only=True)
    rooms = fields.List(fields.Dict(fields.String(),fields.Integer()),required=True,load_only=True)
    to_date = fields.Date(required=True,load_only=True)
    on_hold = fields.Boolean(dump_only=True)
    #expiry_date = fields.DateTime(format="%Y-%m-%d %H:%M", dump_only=True)