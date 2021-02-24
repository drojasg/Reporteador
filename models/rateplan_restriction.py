from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate
from models.restriction import Restriction, RestrictionSchema
from common.util import Util

class RatePlanRestriction(db.Model):
    __tablename__="op_rateplan_restriction"
    __table_args__ = {'extend_existing': True} 

    idop_rateplan_restriction = db.Column(db.Integer,primary_key=True)
    iddef_restriction = db.Column(db.Integer,db.ForeignKey("def_restriction.iddef_restriction"), nullable=False)
    idop_rateplan = db.Column(db.Integer,db.ForeignKey("op_rateplan.idop_rateplan"), nullable=False)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)
    restrictions = db.relationship('Restriction', backref=db.backref('op_rateplan_restriction', lazy=True))

class RatePlanRestrictionSchema(ma.Schema):
    idop_rateplan_restriction = fields.Integer()
    iddef_restriction = fields.Integer(required=True)
    idop_rateplan = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True,validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    restrictions = fields.Nested("RestrictionSchema", many=False, exclude=Util.get_default_excludes())

class GetRatePlanRestrictionSchema(ma.Schema):
    idop_rateplan_restriction = fields.Integer(dump_only=True)
    iddef_restriction = fields.Integer()
    idop_rateplan = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    restrictions = fields.Nested("RestrictionSchema", many=False, exclude=Util.get_default_excludes())