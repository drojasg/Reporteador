from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from .policy_rule import PolicyRule, PolicyRuleSchema
from common.util import Util

class PolicyPenaltyCancelFee(db.Model):
    __tablename__ = "def_policy_penalty_cancel_fee"

    iddef_policy_penalty_cancel_fee = db.Column(db.Integer, primary_key=True)
    iddef_policy_cancel_penalty = db.Column(db.Integer, db.ForeignKey("def_policy_cancel_penalty.iddef_policy_cancel_penalty"), nullable=False)
    iddef_policy_rule = db.Column(db.Integer, db.ForeignKey("def_policy_rule.iddef_policy_rule"), nullable=False)
    policy_rule = db.relationship('PolicyRule', backref=db.backref('def_policy_penalty_cancel_fee', lazy=True))
    percent = db.Column(db.Numeric(5,2), nullable=False, default=0.00)
    option_percent = db.Column(db.Integer, nullable=False, default=0)
    number_nights_percent = db.Column(db.Integer, nullable=False, default=0)
    fixed_amount = db.Column(db.Numeric(15,4), nullable=False, default=0.0000)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class PolicyPenaltyCancelFeeSchema(ma.Schema):
    iddef_policy_penalty_cancel_fee = fields.Integer()
    iddef_policy_cancel_penalty = fields.Integer(required=True)
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

class GetPolicyPenaltyCancelFeeSchema(ma.Schema):
    iddef_policy_penalty_cancel_fee = fields.Integer()
    iddef_policy_cancel_penalty = fields.Integer()
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