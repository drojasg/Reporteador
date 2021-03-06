from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate

class PropertyType(db.Model):
    __tablename__ = "def_property_type"

    iddef_property_type = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)


class PropertyTypeSchema(ma.Schema):
    iddef_property_type = fields.Integer()
    description = fields.String(required=True, validate=validate.Length(max=100))
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
