from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from common.util import Util

class PolicyGuaranteeAntifraud(db.Model):
    __tablename__ = "def_policy_guarantee_antifraud"

    nights_type_one = 1
    nights_type_more_one = 2
    payment_type_fixed_amount = 1
    payment_type_nights = 2

    iddef_policy_guarantee_antifraud = db.Column(db.Integer, primary_key=True)
    iddef_policy_guarantee = db.Column(db.Integer, db.ForeignKey("def_policy_guarantee.iddef_policy_guarantee"), nullable=False)
    guarantee_nights_type = db.Column(db.Integer, nullable=False, default=0)
    guarantee_payment_type = db.Column(db.Integer, nullable=False, default=0)
    amount_payment = db.Column(db.Float, nullable=False, default=0)
    currency_code = db.Column(db.Text(), nullable=False)
    nights_payment = db.Column(db.Integer, nullable=False, default=0)   
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class PolicyGuaranteeAntifraudSchema(ma.Schema):
    iddef_policy_guarantee_antifraud = fields.Integer()
    guarantee_nights_type = fields.Integer()
    guarantee_payment_type = fields.Integer()
    amount_payment = fields.Decimal(as_string=True)
    currency_code = fields.String()
    nights_payment = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")


class DefaultPolicyGuaranteeAntifraudSchema(ma.Schema):
    iddef_policy_guarantee_antifraud = fields.Integer()
    guarantee_nights_type = fields.Integer(required=True)
    guarantee_payment_type = fields.Integer(required=True)
    amount_payment = fields.Decimal(required=True, as_string=True)
    currency_code = fields.String(required=True)
    nights_payment = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
