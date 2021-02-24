from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate
from common.base_audit import BaseAudit

class ExternalCredential(db.Model, BaseAudit):
    __tablename__ = "def_external_credential"

    iddef_external_credential = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    token = db.Column(db.String, nullable=False)
    system_id = db.Column(db.Integer)
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class ExternalCredentialSchema(ma.Schema):
    iddef_external_credential = fields.Integer()
    user = fields.String(required=True, validate=validate.Length(max=50))
    password = fields.String(required=True, validate=validate.Length(max=50))
    token = fields.String(required=True, validate=validate.Length(max=50))
    system_id = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
