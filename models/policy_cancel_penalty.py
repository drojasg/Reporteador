from config import db, ma
from marshmallow import Schema, fields, validate
from models.policy_penalty_cancel_fee import PolicyPenaltyCancelFee, PolicyPenaltyCancelFeeSchema
from datetime import datetime
from common.util import Util
from common.base_audit import BaseAudit

class PolicyCancelPenalty(db.Model, BaseAudit):
    __tablename__ = "def_policy_cancel_penalty"

    iddef_policy_cancel_penalty = db.Column(db.Integer, primary_key=True)
    iddef_policy = db.Column(db.Integer, db.ForeignKey("def_policy.iddef_policy"), nullable=False)
    penalty_name = db.Column(db.String(45), nullable=False)
    days_prior_to_arrival_deadline = db.Column(db.Integer, nullable=False, default=0)
    time_date_deadline = db.Column(db.Time, nullable=False, default="00:00:00")
    description_en = db.Column(db.Text(), nullable=False)
    description_es = db.Column(db.Text(), nullable=False)
    cancel_fees = db.relationship('PolicyPenaltyCancelFee', backref=db.backref('def_policy_cancel_penalty', lazy=True))
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class PolicyCancelPenaltySchema(ma.Schema):
    iddef_policy_cancel_penalty = fields.Integer()
    iddef_policy = fields.Integer(required=True)
    penalty_name = fields.String(validate=validate.Length(max=45))
    days_prior_to_arrival_deadline = fields.Integer(required=True)
    time_date_deadline = fields.Time(required=True)
    description_en = fields.String(required=True)
    description_es = fields.String(required=True)
    cancel_fees = fields.Nested(PolicyPenaltyCancelFeeSchema, many=True, exclude=Util.get_default_excludes())
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class PolicyCancelPenaltyDefaultSchema(ma.Schema):
    iddef_policy_cancel_penalty = fields.Integer()
    iddef_policy = fields.Integer(required=True)
    penalty_name = fields.String(validate=validate.Length(max=45))
    days_prior_to_arrival_deadline = fields.Integer(required=True)
    time_date_deadline = fields.Time(required=True)
    description_en = fields.String(required=True)
    description_es = fields.String(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetPolicyCancelPenaltySchema(ma.Schema):
    iddef_policy_cancel_penalty = fields.Integer()
    iddef_policy = fields.Integer()
    penalty_name = fields.String(validate=validate.Length(max=45))
    days_prior_to_arrival_deadline = fields.Integer()
    time_date_deadline = fields.Time()
    description_en = fields.String()
    description_es = fields.String()
    cancel_fees = fields.Nested(PolicyPenaltyCancelFeeSchema, many=True, exclude=Util.get_default_excludes())
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetPolicyCancelPenaltyDefaultSchema(ma.Schema):
    iddef_policy_cancel_penalty = fields.Integer()
    iddef_policy = fields.Integer()
    penalty_name = fields.String(validate=validate.Length(max=45))
    days_prior_to_arrival_deadline = fields.Integer(required=True)
    time_date_deadline = fields.Time()
    description_en = fields.String()
    description_es = fields.String()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")