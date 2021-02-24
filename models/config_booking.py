from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from common.util import Util

class ConfigBooking(db.Model):
    __tablename__ = "config_booking"
    idconfig_booking = db.Column(db.Integer, primary_key=True)
    enable_public = db.Column(db.Integer, nullable=False)
    param = db.Column(db.String(50), nullable=False)
    value = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)    

class ConfigBookingSchema(ma.Schema):
    idconfig_booking = fields.Integer()
    idbook_status = fields.Integer()
    param = fields.String(required=False, validate=validate.Length(max=50))
    value = fields.String(required=False, validate=validate.Length(max=50))
    type = fields.String(required=False, validate=validate.Length(max=50))
    enable_public = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
