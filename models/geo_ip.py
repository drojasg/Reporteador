from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate
from common.base_audit import BaseAudit

class GeoIp(db.Model, BaseAudit):
    __tablename__ = "op_geo_ip"
    
    idop_geo_ip = db.Column(db.Integer, primary_key=True)
    start_ip_address = db.Column(db.String(50), nullable=False)
    end_ip_address = db.Column(db.String(50), nullable=False)    
    start_ip_numeric = db.Column(db.Integer)
    end_ip_numeric = db.Column(db.Integer)
    country_code_iso_2 = db.Column(db.String(2), nullable=False)
    country_code_iso_3 = db.Column(db.String(3), nullable=False)
    country_code_iso_number = db.Column(db.Integer)
    country_name = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)


class GeoIpSchema(ma.Schema):

    class Meta:
        ordered = True

    idop_geo_ip = fields.Integer()
    #start_ip_address = fields.String(required=True, validate=validate.Length(max=50))
    #end_ip_address = fields.String(required=True, validate=validate.Length(max=50))
    #start_ip_numeric = fields.Integer()
    #end_ip_numeric = fields.Integer()
    country_code_iso_2 = fields.String(required=True, validate=validate.Length(max=2))
    country_code_iso_3 = fields.String(required=True, validate=validate.Length(max=3))
    country_code_iso_number = fields.Integer()
    country_name = fields.String(required=True, validate=validate.Length(max=100))
    default_currency = fields.String(dump_only=True)
    iddefault_currency = fields.Integer(dump_only=True)
    #estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")