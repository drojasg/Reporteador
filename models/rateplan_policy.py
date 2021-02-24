from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate
from common.util import Util

class RatePlanPolicy(db.Model):
    __tablename__="op_rateplan_policy"
    __table_args__ = {'extend_existing': True} 

    idop_rateplan_policy = db.Column(db.Integer,primary_key=True)
    idop_rateplan = db.Column(db.Integer,db.ForeignKey("op_rateplan.idop_rateplan"), nullable=False)
    iddef_policy = db.Column(db.Integer,db.ForeignKey("def_policy.iddef_policy"), nullable=False)
    iddef_policy_category = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class RatePlanPropertySchema(ma.Schema):
    idop_rateplan_policy = fields.Integer()
    idop_rateplan = fields.Integer(required=True)
    iddef_policy = fields.Integer(required=True)
    iddef_policy_category = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")