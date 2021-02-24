from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from common.util import Util
from common.base_audit import BaseAudit

class PolicyGuaranteeType(db.Model, BaseAudit):
    __tablename__ = "def_policy_guarantee_type"

    iddef_policy_guarantee_type = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(45), nullable=False)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class PolicyGuaranteeTypeSchema(ma.Schema):
    iddef_policy_guarantee_type = fields.Integer()
    description = fields.String(validate=validate.Length(max=45), required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetPolicyGuaranteeTypeSchema(ma.Schema):
    iddef_policy_guarantee_type = fields.Integer()
    description = fields.String(validate=validate.Length(max=45))
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")