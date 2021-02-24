from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from common.util import Util

class PolicyTaxPrice(db.Model):
    __tablename__ = "def_policy_tax_price"

    iddef_policy_tax_price = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(300), nullable=False)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class PolicyTaxPriceSchema(ma.Schema):
    iddef_policy_tax_price = fields.Integer()
    description = fields.String(validate=validate.Length(max=300), required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetPolicyTaxPriceSchema(ma.Schema):
    iddef_policy_tax_price = fields.Integer()
    description = fields.String(validate=validate.Length(max=300))
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")