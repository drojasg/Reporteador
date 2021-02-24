from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from common.util import Util
from models.policy import Policy, PolicySchema
from models.market_segment import MarketSegment, MarketSegmentSchema
from common.base_audit import BaseAudit

class PolicyPayment(db.Model, BaseAudit):
    __tablename__ ="def_policy_payment_1"

    iddef_policy_payment = db.Column(db.Integer, primary_key=True)
    iddef_policy = db.Column(db.Integer, db.ForeignKey("def_policy.iddef_policy"), nullable=False)
    #COLUMNAS NUEVAS
    market_segment_list = db.Column(db.JSON, nullable=False)
    property_list = db.Column(db.JSON, nullable=False)
    #
    description_en = db.Column(db.String(9000), nullable= False)
    description_es = db.Column(db.String(9000), nullable = False)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow) 

class PolicyPaymentSchema(ma.Schema):
    iddef_policy_payment = fields.Integer()
    iddef_policy = fields.Integer()
    #
    market_segment_list = fields.Dict(required=True)#fields.List(fields.Integer())
    property_list = fields.Dict(required=True) #fields.List(fields.Integer())
    #
    description_en = fields.String(validate=validate.Length(max=9000))
    description_es = fields.String(validate=validate.Length(max=9000))
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetPolicyPaymentSchema(ma.Schema):
    iddef_policy_payment = fields.Integer()
    #
    market_segment_list = fields.Dict(required=True)#fields.List(fields.Integer())
    property_list = fields.Dict(required=True) #fields.List(fields.Integer())
    
    #
    iddef_policy = fields.Integer()
    iddef_market_segment = fields.Integer()
    description_en = fields.String(validate=validate.Length(max=9000))
    description_es = fields.String(validate=validate.Length(max=9000))
    estado = fields.Integer()
    policy_code = fields.String(validate=validate.Length(max=45))
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")


class PolicyPaymentCreateUpdateSchema(ma.Schema):
    policy_code = fields.String()
    #iddef_policy = fields.String()
    #
    market_segment_list = fields.Dict(required=True)#fields.List(fields.Integer())
    property_list = fields.Dict(required=True) #fields.List(fields.Integer())
    
    #
    description_en = fields.String()
    description_es = fields.String()
    estado = fields.Int(default=1, required= False)