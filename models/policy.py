from config import db, ma
from marshmallow import Schema, fields, validate
from models.currency import Currency
from models.policy_category import PolicyCategory
#from models.policy_cancel_penalty import PolicyCancelPenalty, PolicyCancelPenaltySchema
from models.policy_cancellation_detail import PolicyCancellationDetail, PolicyCancellationDetailSchema
from models.policy_tax_group import PolicyTaxGroup, PolicyTaxGroupSchema
from models.policy_guarantee import PolicyGuarantee, PolicyGuaranteeSchema
from datetime import datetime
from common.util import Util

class Policy(db.Model):
    __tablename__ = "def_policy"

    iddef_policy = db.Column(db.Integer, primary_key=True)
    policy_code = db.Column(db.String(45), nullable=False)
    iddef_currency = db.Column(db.Integer, db.ForeignKey("def_currency.iddef_currency"), nullable=False)
    currency_code = db.relationship('Currency', backref=db.backref('def_policy', lazy=True))
    iddef_policy_category = db.Column(db.Integer, db.ForeignKey("def_policy_category.iddef_policy_category"), nullable=False)
    policy_category = db.relationship('PolicyCategory', backref=db.backref('def_policy', lazy=True))
    is_default = db.Column(db.Integer, nullable=False)
    option_selected = db.Column(db.Integer, nullable=False)
    text_only_policy = db.Column(db.Integer, nullable=False)
    available_dates = db.Column(db.JSON, nullable=False, default=[])
    policy_cancel_penalties = db.relationship('PolicyCancellationDetail', backref=db.backref('policy', lazy=True))
    #policy_cancel_penalties = db.relationship('PolicyCancelPenalty', backref=db.backref('policy', lazy=True))
    policy_guarantees = db.relationship('PolicyGuarantee', backref=db.backref('policy', lazy=True))
    policy_tax_groups = db.relationship('PolicyTaxGroup', backref=db.backref('policy', lazy=True))
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class GetPolicyPublicSchema(ma.Schema):
    iddef_policy = fields.Integer()
    policy_code = fields.String(validate=validate.Length(max=45))
    iddef_policy_category = fields.Integer()

class PolicySchema(ma.Schema):
    iddef_policy = fields.Integer()
    policy_code = fields.String(validate=validate.Length(max=45))
    iddef_currency = fields.Integer(required=True)
    currency_code = ma.Pluck("CurrencySchema", "currency_code")
    iddef_policy_category = fields.Integer(required=True)
    policy_category = ma.Pluck("PolicyCategorySchema", 'description')
    is_default = fields.Integer(required=True)
    option_selected = fields.Integer(required=True)
    text_only_policy = fields.Integer(required=True)
    available_dates = fields.List(fields.Dict())
    #policy_cancel_penalties = fields.Nested(PolicyCancelPenaltySchema, many=True, exclude=Util.get_default_excludes())
    policy_guarantees = fields.Nested(PolicyGuaranteeSchema, many=True, exclude=Util.get_default_excludes())
    policy_tax_groups = fields.Nested(PolicyTaxGroupSchema, many=True, exclude=Util.get_default_excludes())
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetPolicySchema(ma.Schema):
    iddef_policy = fields.Integer()
    policy_code = fields.String(validate=validate.Length(max=45))
    iddef_currency = fields.Integer()
    currency_code = ma.Pluck("CurrencySchema", "currency_code")
    iddef_policy_category = fields.Integer()
    policy_category = ma.Pluck("PolicyCategorySchema", 'description')
    is_default = fields.Integer()
    option_selected = fields.Integer()
    text_only_policy = fields.Integer()
    available_dates = fields.List(fields.Dict())
    #policy_cancel_penalties = fields.Nested(PolicyCancelPenaltySchema, many=True, exclude=Util.get_default_excludes())
    policy_guarantees = fields.Nested(PolicyGuaranteeSchema, many=True, exclude=Util.get_default_excludes())
    policy_tax_groups = fields.Nested(PolicyTaxGroupSchema, many=True, exclude=Util.get_default_excludes())
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class PolicyCPSchema(ma.Schema):
    iddef_policy = fields.Integer()
    policy_code = fields.String(validate=validate.Length(max=45))
    iddef_currency = fields.Integer(required=True)
    currency_code = ma.Pluck("CurrencySchema", "currency_code")
    iddef_policy_category = fields.Integer(required=True)
    policy_category = ma.Pluck("PolicyCategorySchema", 'description')
    is_default = fields.Integer(required=True)
    option_selected = fields.Integer(required=True)
    text_only_policy = fields.Integer(required=True)
    available_dates = fields.List(fields.Dict())
    policy_cancel_penalties = fields.List(fields.Nested(PolicyCancellationDetailSchema, exclude=Util.get_default_excludes()))
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetPolicyCPSchema(ma.Schema):
    iddef_policy = fields.Integer()
    policy_code = fields.String(validate=validate.Length(max=45))
    iddef_currency = fields.Integer()
    currency_code = ma.Pluck("CurrencySchema", "currency_code")
    iddef_policy_category = fields.Integer()
    policy_category = ma.Pluck("PolicyCategorySchema", 'description')
    is_default = fields.Integer()
    option_selected = fields.Integer()
    text_only_policy = fields.Integer()
    available_dates = fields.List(fields.Dict())
    #policy_cancel_penalties = fields.Nested(PolicyCancelPenaltySchema, many=True, exclude=Util.get_default_excludes())
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class PolicyGSchema(ma.Schema):
    iddef_policy = fields.Integer()
    policy_code = fields.String(validate=validate.Length(max=45))
    iddef_currency = fields.Integer(required=True)
    currency_code = ma.Pluck("CurrencySchema", "currency_code")
    iddef_policy_category = fields.Integer(required=True)
    policy_category = ma.Pluck("PolicyCategorySchema", 'description')
    is_default = fields.Integer(required=True)
    option_selected = fields.Integer(required=True)
    text_only_policy = fields.Integer(required=True)
    available_dates = fields.List(fields.Dict())
    policy_guarantees = fields.Nested(PolicyGuaranteeSchema, many=True, exclude=Util.get_default_excludes())
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetPolicyGSchema(ma.Schema):
    iddef_policy = fields.Integer()
    policy_code = fields.String(validate=validate.Length(max=45))
    iddef_currency = fields.Integer()
    currency_code = ma.Pluck("CurrencySchema", "currency_code")
    iddef_policy_category = fields.Integer()
    policy_category = ma.Pluck("PolicyCategorySchema", 'description')
    is_default = fields.Integer()
    option_selected = fields.Integer()
    text_only_policy = fields.Integer()
    available_dates = fields.List(fields.Dict())
    policy_guarantees = fields.Nested(PolicyGuaranteeSchema, many=True, exclude=Util.get_default_excludes())
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class PolicyTSchema(ma.Schema):
    iddef_policy = fields.Integer()
    policy_code = fields.String(validate=validate.Length(max=45))
    iddef_currency = fields.Integer(required=True)
    currency_code = ma.Pluck("CurrencySchema", "currency_code")
    iddef_policy_category = fields.Integer(required=True)
    policy_category = ma.Pluck("PolicyCategorySchema", 'description')
    is_default = fields.Integer(required=True)
    option_selected = fields.Integer(required=True)
    text_only_policy = fields.Integer(required=True)
    available_dates = fields.List(fields.Dict())
    policy_tax_groups = fields.Nested(PolicyTaxGroupSchema, many=True, exclude=Util.get_default_excludes())
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetPolicyTSchema(ma.Schema):
    iddef_policy = fields.Integer()
    policy_code = fields.String(validate=validate.Length(max=45))
    iddef_currency = fields.Integer()
    currency_code = ma.Pluck("CurrencySchema", "currency_code")
    iddef_policy_category = fields.Integer()
    policy_category = ma.Pluck("PolicyCategorySchema", 'description')
    is_default = fields.Integer()
    option_selected = fields.Integer()
    text_only_policy = fields.Integer()
    available_dates = fields.List(fields.Dict())
    policy_tax_groups = fields.Nested(PolicyTaxGroupSchema, many=True, exclude=Util.get_default_excludes())
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class PolicyPostSchema(ma.Schema):
    iddef_policy = fields.Integer()
    #iddef_property = fields.Integer()
    policy_code = fields.String(validate=validate.Length(max=45))
    iddef_currency = fields.Integer(required=True)
    currency_code = ma.Pluck("CurrencySchema", "currency_code")
    iddef_policy_category = fields.Integer(required=True)
    policy_category = ma.Pluck("PolicyCategorySchema", 'description')
    is_default = fields.Integer(required=True)
    option_selected = fields.Integer(required=True)
    text_only_policy = fields.Integer(required=True)
    available_dates = fields.List(fields.Dict())
    #policy_cancel_penalties = fields.Nested(PolicyCancelPenaltySchema, many=True, exclude=Util.get_default_excludes())
    policy_guarantees = fields.Nested(PolicyGuaranteeSchema, many=True, exclude=Util.get_default_excludes())
    policy_tax_groups = fields.Nested(PolicyTaxGroupSchema, many=True, exclude=Util.get_default_excludes())
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class PolicyPostDefaultSchema(ma.Schema):
    iddef_policy = fields.Integer()
    #iddef_property = fields.Integer()
    policy_code = fields.String(validate=validate.Length(max=45))
    iddef_currency = fields.Integer(required=True)
    currency_code = ma.Pluck("CurrencySchema", "currency_code")
    iddef_policy_category = fields.Integer(required=True)
    policy_category = ma.Pluck("PolicyCategorySchema", 'description')
    is_default = fields.Integer(required=True)
    option_selected = fields.Integer(required=True)
    text_only_policy = fields.Integer(required=True)
    available_dates = fields.List(fields.Dict())
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetPolicyDefaultSchema(ma.Schema):
    iddef_policy = fields.Integer()
    policy_code = fields.String(validate=validate.Length(max=45))
    iddef_currency = fields.Integer()
    currency_code = ma.Pluck("CurrencySchema", "currency_code")
    iddef_policy_category = fields.Integer()
    policy_category = ma.Pluck("PolicyCategorySchema", 'description')
    is_default = fields.Integer()
    option_selected = fields.Integer()
    text_only_policy = fields.Integer()
    available_dates = fields.List(fields.Dict())
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class PolicyRatePlanSchema(ma.Schema):
    iddef_policy = fields.Integer()
    policy_code = fields.String(validate=validate.Length(max=45))
    #iddef_policy_category = fields.Integer(required=True)
    policy_category = ma.Pluck("PolicyCategorySchema", 'description')
    is_default = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetPolicyRatePlanSchema(ma.Schema):
    lang_code = fields.String(required=True, validate=validate.Length(max=10))
    id_rateplans = fields.List(fields.Integer(), required=True)