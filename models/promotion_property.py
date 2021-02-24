from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate
from models.promotions import Promotions
from models.property import Property
from common.util import Util
from common.base_audit import BaseAudit

class PromotionProperty(db.Model, BaseAudit):
    __tablename__ = "op_promotion_property"

    idop_promotion_property = db.Column(db.Integer, primary_key=True)
    id_promotion = db.Column(db.Integer,db.ForeignKey("op_promotions.idop_promotions"), nullable=False)
    promotions_property = db.relationship('Promotions', backref=db.backref('op_promotion_property', lazy="dynamic"))
    id_property = db.Column(db.Integer,db.ForeignKey("def_property.iddef_property"), nullable=False)
    property = db.relationship('Property', backref=db.backref('op_promotion_property', lazy="dynamic"))
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)


class PromotionPropertySchema(ma.Schema):
    idop_promotion_property = fields.Integer()
    id_promotion = fields.Integer(required=True)
    promotions_property =  ma.Nested("PromotionsSchema",exclude=Util.get_default_excludes())
    id_property = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetPromotionPropertySchema(ma.Schema):
    idop_promotion_property = fields.Integer()
    id_promotion = fields.Integer()
    id_property = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class SearchPromotionPropertySchema(ma.Schema):
    idop_promotion_property = fields.Integer(load_only=True)
    id_promotion = fields.Integer(load_only=True)
    promotions_property =  ma.Nested("PromotionsSchema",exclude=Util.get_default_excludes())
    id_property = fields.Integer(load_only=True)
    property = ma.Pluck("PropertySchema", 'property_code')
    estado = fields.Integer(load_only=True)
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
