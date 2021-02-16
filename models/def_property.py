from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate

class Property(db.Model):
    __tablename__ = "def_property"

    iddef_property = db.Column(db.Integer, primary_key=True)
    short_name = db.Column(db.String(45), nullable=False)
    trade_name = db.Column(db.String(45), nullable=False)
    property_code = db.Column(db.String(6), nullable=False)
    web_address = db.Column(db.String(300), nullable=False)
    iddef_brand = db.Column(db.Integer)
    iddef_property_type = db.Column(db.Integer)
    push_property = db.Column(db.Integer)
    icon_logo_name = db.Column(db.String(50), nullable=False)
    iddef_time_zone = db.Column(db.Integer)
    sender = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)


class PropertySchema(ma.Schema):

    iddef_property = fields.Integer()
    short_name = fields.String(required=True, validate=validate.Length(max=45))
    trade_name = fields.String(required=True, validate=validate.Length(max=45))
    property_code = fields.String(required=True, validate=validate.Length(max=6))
    web_address = fields.String(required=True, validate=validate.Length(max=300))
    iddef_brand = fields.Integer()
    iddef_property_type = fields.Integer()
    push_property = fields.Integer()
    icon_logo_name = fields.String(required=True, validate=validate.Length(max=50))
    iddef_time_zone = fields.Integer()
    sender = fields.String(required=True, validate=validate.Length(max=50))
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
