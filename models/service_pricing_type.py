from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate
from models.service_pricing_option import ServicePricingOption, ServicePricingOptionSchema, GetServicePricingOptionSchema
from common.util import Util

class ServicePricingType(db.Model):
    __tablename__ = "def_service_pricing_type"
    
    iddef_service_pricing_type = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String, nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)
    #options = db.relationship('ServicePricingOption', backref=db.backref('service_pricing_type', lazy=True))

class ServicePricingTypeSchema(ma.Schema):
    iddef_service_pricing_type = fields.Integer()
    description = fields.String(required=True, validate=validate.Length(max=150))
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    options = fields.List(fields.Nested("ServicePricingOptionSchema", exclude=Util.get_default_excludes()),required=True, many=True)

class GetServicePricingTypeSchema(ma.Schema):
    iddef_service_pricing_type = fields.Integer()
    description = fields.String(validate=validate.Length(max=150))
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    options = fields.List(fields.Integer(),required=True)
    #options = fields.List(fields.Nested("GetServicePricingOptionSchema", exclude=Util.get_default_excludes()),required=True, many=True)