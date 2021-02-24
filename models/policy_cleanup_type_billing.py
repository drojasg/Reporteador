from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from common.util import Util
from common.base_audit import BaseAudit

class PolicyCleanupTypeBilling(db.Model, BaseAudit):
    __tablename__ = "def_policy_cleanup_type_billing"

    iddef_policy_cleanup_type_billing = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(300), nullable=False)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class PolicyCleanupTypeBillingSchema(ma.Schema):
    iddef_policy_cleanup_type_billing = fields.Integer()
    description = fields.String(validate=validate.Length(max=300), required=True, required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetPolicyCleanupTypeBillingSchema(ma.Schema):
    iddef_policy_cleanup_type_billing = fields.Integer()
    description = fields.String(validate=validate.Length(max=300))
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")