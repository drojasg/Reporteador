from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate
from models.promotions import Promotions
from models.rateplan import RatePlan
from models.property import Property
from common.util import Util

class PromotionRateplan(db.Model):
    __tablename__="def_promotion_rateplan"
    __table_args__ = {'extend_existing': True} 

    iddef_promotion_rateplan = db.Column(db.Integer,primary_key=True)
    id_promotion = db.Column(db.Integer,db.ForeignKey("op_promotions.idop_promotions"), nullable=False)
    id_rateplan = db.Column(db.Integer,db.ForeignKey("op_rateplan.idop_rateplan"), nullable=False)
    id_property = db.Column(db.Integer,db.ForeignKey("def_property.iddef_property"), nullable=False)
    rate_plan_rooms = db.Column(db.JSON(), nullable=False, default=[])
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class PromotionRateplanSchema(ma.Schema):
    iddef_promotion_rateplan = fields.Integer()
    id_promotion = fields.Integer(required=True)
    id_rateplan = fields.Integer(required=True)
    id_property = fields.Integer(required=True)
    rate_plan_rooms = fields.Dict()
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")