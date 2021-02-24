from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate

class ServicePricingOption(db.Model):
    __tablename__ = "def_service_pricing_option"
    
    iddef_service_pricing_option = db.Column(db.Integer, primary_key=True)
    #iddef_pricing_type = db.Column(db.Integer, nullable=False)
    iddef_pricing_type = db.Column(db.Integer, db.ForeignKey('def_service_pricing_type.iddef_service_pricing_type'), nullable=False)
    name = db.Column(db.String, nullable=False)
    formula = db.Column(db.String, nullable=False, default="")
    params = db.Column(db.JSON(), nullable=False, default=[])
    price = db.Column(db.Integer, nullable=False, default=0.00)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class ServicePricingOptionSchema(ma.Schema):
    iddef_service_pricing_option = fields.Integer()
    iddef_pricing_type = fields.Integer()
    name = fields.String(required=True, validate=validate.Length(max=150))
    formula = fields.String(validate=validate.Length(max=250))
    params = fields.List(fields.Dict())
    price = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetServicePricingOptionSchema(ma.Schema):
    iddef_service_pricing_option = fields.Integer()
    iddef_pricing_type = fields.Integer()
    name = fields.String(validate=validate.Length(max=150))
    formula = fields.String(validate=validate.Length(max=250))
    params = fields.List(fields.Dict())
    price = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class ParamsSchema(ma.Schema):
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    price = fields.Float(required=True)
    minimo = fields.Integer(required=True)
    maximo = fields.Integer(required=True)