from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate
from common.util import Util

class AmenityGroup(db.Model):
    __tablename__ = "def_amenity_group"

    iddef_amenity_group = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45))
    description = db.Column(db.String(45))
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)


class AmenityGroupSchema(ma.Schema):
    iddef_amenity_group = fields.Integer()
    name = fields.String(required=False,validate=validate.Length(max=45))
    description = fields.String(required=False,validate=validate.Length(max=45))
    estado = fields.Integer()
    usuario_creacion = fields.String(required=False, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetAmenityGroupSchema(ma.Schema):
    iddef_amenity_group = fields.Integer()
    name = fields.String(validate=validate.Length(max=45))
    description = fields.String(validate=validate.Length(max=45))
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class getNameGroupSchema(ma.Schema):
    name= fields.String()
