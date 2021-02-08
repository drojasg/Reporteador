from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate

class AreaUnit(db.Model):
    __tablename__ = "def_area_unit"

    iddef_area_unit = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(100), nullable=False)
    unit_code = db.Column(db.String(45))
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)


class AreaUnitSchema(ma.Schema):
    iddef_area_unit = fields.Integer()
    description = fields.String(required=True, validate=validate.Length(max=100))
    unit_code = fields.String(required=True, validate=validate.Length(max=45))
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
