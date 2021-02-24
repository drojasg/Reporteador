from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate
from models.rateplan import RatePlan, RatePlanSchema
from common.util import Util

class RatePlanProperty(db.Model):
    __tablename__="op_rateplan_property"
    __table_args__ = {'extend_existing': True} 

    idop_rateplan_property = db.Column(db.Integer,primary_key=True)
    id_rateplan = db.Column(db.Integer,db.ForeignKey("op_rateplan.idop_rateplan"), nullable=False)
    id_property = db.Column(db.Integer,db.ForeignKey("def_property.iddef_property"), nullable=False)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)
    #rateplans = db.relationship('RatePlanSchema', backref=db.backref('op_rate_plan_property', lazy=True))

class RatePlanPropertySchema(ma.Schema):
    idop_rateplan_property = fields.Integer()
    id_rateplan = fields.Integer(required=True)
    id_property = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    #rateplans = fields.Nested("RatePlanSchema", many=False, exclude=Util.get_default_excludes())