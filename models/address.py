from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from common.util import Util

class Address(db.Model):
    __tablename__ = "def_address"

    iddef_address = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(250), nullable=False)
    latitude = db.Column(db.String(45), nullable=False)
    longitude = db.Column(db.String(45), nullable=False)
    country_code = db.Column(db.String(10), nullable=False)
    state_code = db.Column(db.String(10), nullable=False)
    zip_code = db.Column(db.String(12), nullable=False)
    city = db.Column(db.String(150), nullable=False)
    iddef_contact = db.Column(db.Integer, db.ForeignKey('def_contact.iddef_contact'), nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class AddressSchema(ma.Schema):
    iddef_address = fields.Integer()
    address = fields.String(required=True, validate=validate.Length(max=250))
    latitude = fields.String(validate=validate.Length(max=45))
    longitude = fields.String(validate=validate.Length(max=45))
    country_code = fields.String(required=True, validate=validate.Length(max=10))
    state_code = fields.String(validate=validate.Length(max=10))
    zip_code = fields.String(validate=validate.Length(max=12))
    city = fields.String(validate=validate.Length(max=150))
    iddef_contact = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")