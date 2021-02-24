from datetime import datetime
from enum import Enum
from config import db, ma
from marshmallow import Schema, fields, validate

class ExternalServicesEnum(Enum):
    dev = "dev"
    qa = "qa"
    pro = "pro"

class ConfigExternalServices(db.Model):
    __tablename__ = "config_external_services"
    __table_args__ = {'extend_existing': True}

    idconfig_external_services = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    code = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    env = db.Column(db.Enum(ExternalServicesEnum), nullable=False)
    settings = db.Column(db.JSON(), nullable=False)
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)


class ConfigExternalServicesSchema(ma.Schema):
    idconfig_external_services = fields.Integer()
    name = fields.String(required=True, validate=validate.Length(max=50))
    code = fields.String(required=True, validate=validate.Length(max=50))
    url = fields.String(required=True, validate=validate.Length(max=200))
    env = fields.String(required=True, validate=validate.Length(max=10))
    settings = fields.Dict()
    estado = fields.Integer()
    usuario_creacion = fields.String(
        required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(
        validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
