from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from .policy_rule import PolicyRule, PolicyRuleSchema
from common.util import Util

class PolicyGuaranteeDeposit(db.Model):
    __tablename__ = "def_policy_guarantee_deposit"

    iddef_policy_guarantee_deposit = db.Column(db.Integer, primary_key=True)
    iddef_policy_guarantee = db.Column(db.Integer, db.ForeignKey("def_policy_guarantee.iddef_policy_guarantee"), nullable=False)
    iddef_policy_rule = db.Column(db.Integer, db.ForeignKey("def_policy_rule.iddef_policy_rule"), nullable=False)
    policy_rule = db.relationship('PolicyRule', backref=db.backref('def_policy_guarantee_deposit', lazy=True))
    percent = db.Column(db.Numeric(5,2), nullable=False, default=0.00)
    option_percent = db.Column(db.Integer, nullable=False, default=0)
    number_nights_percent = db.Column(db.Integer, nullable=False)
    fixed_amount = db.Column(db.Numeric(15,2), nullable=False, default=0.00)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class PolicyGuaranteeDepositSchema(ma.Schema):
    iddef_policy_guarantee_deposit = fields.Integer()
    iddef_policy_guarantee = fields.Integer(required=True)
    iddef_policy_rule = fields.Integer(required=True)
    policy_rule = ma.Pluck("PolicyRuleSchema", "description")
    percent = fields.Decimal(required=True, as_string=True)
    option_percent = fields.Integer(required=True)
    number_nights_percent = fields.Integer(required=True)
    fixed_amount = fields.Decimal(required=True, as_string=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetPolicyGuaranteeDepositSchema(ma.Schema):
    iddef_policy_guarantee_deposit = fields.Integer()
    iddef_policy_guarantee = fields.Integer()
    iddef_policy_rule = fields.Integer()
    policy_rule = ma.Pluck("PolicyRuleSchema", "description")
    percent = fields.Decimal(as_string=True)
    option_percent = fields.Integer()
    number_nights_percent = fields.Integer()
    fixed_amount = fields.Decimal(as_string=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")