from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate
from models.service_pricing_type import ServicePricingType, ServicePricingTypeSchema
from models.service_price import ServicePrice, ServicePriceSchema, GetServicePriceSchema
from models.currency import Currency, CurrencySchema
from models.property import Property
from common.util import Util

class Service(db.Model):
    __tablename__ = "def_service"
    
    iddef_service = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    service_code = db.Column(db.String, nullable=False)
    iddef_tax_rule_group = db.Column(db.Integer, default="0")
    iddef_pricing_type = db.Column(db.Integer,db.ForeignKey("def_service_pricing_type.iddef_service_pricing_type"), nullable=False)
    service_pricing_type = db.relationship('ServicePricingType', backref=db.backref('def_service', lazy="dynamic"))
    pricing_option = db.Column(db.JSON(), nullable=False, default={})
    is_same_price_all_dates = db.Column(db.Integer, nullable=False)
    available_upon_request = db.Column(db.Integer, nullable=False)
    auto_add_price_is_zero = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)
    iddef_property = db.Column(db.Integer,db.ForeignKey("def_property.iddef_property"), nullable=False)
    property = db.relationship('Property', backref=db.backref('def_service', lazy="dynamic"))
    html_icon = db.Column(db.String(50), nullable=False)
    iddef_currency = db.Column(db.Integer,db.ForeignKey("def_currency.iddef_currency"), nullable=False)
    service_currency = db.relationship('Currency', backref=db.backref('def_service', lazy="dynamic"))

class ServiceSchema(ma.Schema):
    iddef_service = fields.Integer()
    name = fields.String(required=True, validate=validate.Length(max=150))
    service_code = fields.String(required=True, validate=validate.Length(max=45))
    iddef_tax_rule_group = fields.Integer()
    iddef_pricing_type = fields.Integer()
    pricing_option = fields.Raw()
    is_same_price_all_dates = fields.Integer()
    available_upon_request = fields.Integer()
    auto_add_price_is_zero = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    service_pricing_type = ma.Pluck("ServicePricingTypeSchema", 'description')
    iddef_property = fields.Integer()
    property = ma.Pluck("PropertySchema", 'property_code')
    html_icon = fields.String(
        required=True, validate=validate.Length(max=50))
    iddef_currency = fields.Integer(required=True)

class ServicePublicSchema(ma.Schema):
    iddef_service = fields.Integer()
    name = fields.String(required=True, validate=validate.Length(max=150))
    service_code = fields.String(required=True, validate=validate.Length(max=45))
    iddef_tax_rule_group = fields.Integer()
    iddef_pricing_type = fields.Integer()
    pricing_option = fields.Raw()
    is_same_price_all_dates = fields.Integer()
    available_upon_request = fields.Integer()
    auto_add_price_is_zero = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    service_pricing_type = ma.Pluck("ServicePricingTypeSchema", 'description')
    iddef_property = fields.Integer()
    html_icon = fields.String(
        required=True, validate=validate.Length(max=50))
    iddef_currency = fields.Integer()
    price = fields.Float()
    service_info = fields.String()
    min_los = fields.Integer()
    max_los = fields.Integer()

class GetDataTextLangSchema(ma.Schema):
    language_code = fields.String(validate=validate.Length(max=10))
    datos_lang = fields.Nested("GetDataContentSchema", many=True)
    data_media = fields.List(fields.Integer(),required=True)

class GetDataContentSchema(ma.Schema):
    Name = fields.String(required=True)
    Teaser = fields.String()
    Description = fields.String(required=True)
    icon_description = fields.String(required=True)

class SaveServiceSchema(ma.Schema):
    iddef_service = fields.Integer()
    name = fields.String(required=True, validate=validate.Length(max=150))
    service_code = fields.String(required=True, validate=validate.Length(max=45))
    iddef_tax_rule_group = fields.Integer()
    iddef_pricing_type = fields.Integer()
    is_same_price_all_dates = fields.Integer()
    available_upon_request = fields.Integer()
    auto_add_price_is_zero = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    datos_pricing_option = fields.Raw()
    datos_cont_lang = fields.List(fields.Nested("GetDataTextLangSchema"),required=True, many=True)
    datos_services = fields.List(fields.Nested("ServicePriceSchema"),required=True)
    datos_restriction = fields.List(fields.Integer(),required=True)
    iddef_property = fields.Integer(required=True)
    html_icon = fields.String(validate=validate.Length(max=50))
    iddef_currency = fields.Integer(required=True)

class UpdateServiceSchema(ma.Schema):
    iddef_service = fields.Integer()
    name = fields.String(required=True, validate=validate.Length(max=150))
    service_code = fields.String(required=True, validate=validate.Length(max=45))
    iddef_tax_rule_group = fields.Integer()
    iddef_pricing_type = fields.Integer()
    is_same_price_all_dates = fields.Integer()
    available_upon_request = fields.Integer()
    auto_add_price_is_zero = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    datos_pricing_option = fields.Raw(required=True)
    datos_cont_lang = fields.List(fields.Nested("GetDataTextLangSchema"),required=True, many=True)
    datos_services = fields.List(fields.Nested("ServicePriceSchema"),required=True)
    datos_restriction = fields.List(fields.Integer(),required=True)
    iddef_property = fields.Integer(required=True)
    html_icon = fields.String(validate=validate.Length(max=50))
    iddef_currency = fields.Integer(required=True)

class GetPublicServiceSchema(ma.Schema):
    lang_code = fields.String(validate=validate.Length(max=10))
    date_start = fields.DateTime("%Y-%m-%d", required=True)
    date_end = fields.DateTime("%Y-%m-%d", required=True)
    market = fields.String(validate=validate.Length(max=15))
    currency_code = fields.String(validate=validate.Length(max=10))
    id_hotel = fields.String(required=True, validate=validate.Length(max=6))
    rooms = fields.List(fields.Dict(fields.String(),fields.Integer()))
    services = fields.List(fields.Integer())