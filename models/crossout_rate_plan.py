from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate
from models.cross_out_config import CrossOutConfig, CrossOutConfigSchema
from common.util import Util

class CrossoutRatePlan(db.Model):
    __tablename__="op_crossout_rate_plan"
    __table_args__ = {'extend_existing': True} 

    idop_crossout_rate_plan = db.Column(db.Integer,primary_key=True)
    iddef_crossout = db.Column(db.Integer,db.ForeignKey("op_cross_out_config.idop_cross_out_config"), nullable=False)
    iddef_rate_plan = db.Column(db.Integer,db.ForeignKey("op_rateplan.idop_rateplan"), nullable=False)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)
    crossouts = db.relationship('CrossOutConfig', backref=db.backref('op_crossout_rate_plan', lazy=True))

class CrossoutRatePlanSchema(ma.Schema):
    idop_crossout_rate_plan = fields.Integer()
    iddef_crossout = fields.Integer(required=True)
    iddef_rate_plan = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True,validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    crossouts = fields.Nested("CrossOutConfigSchema", many=False, exclude=Util.get_default_excludes())

class GetCrossoutRatePlanSchema(ma.Schema):
    idop_crossout_rate_plan = fields.Integer(dump_only=True)
    iddef_crossout = fields.Integer()
    iddef_rate_plan = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    crossouts = fields.Nested("CrossOutConfigSchema", many=False, exclude=Util.get_default_excludes())