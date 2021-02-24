from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate
from models.promotions import Promotions
from models.restriction import Restriction
from common.util import Util

class PromotionRestriction(db.Model):
    __tablename__ = "op_promotion_restriction"

    idop_promotion_restriction = db.Column(db.Integer, primary_key=True)
    id_promotion = db.Column(db.Integer,db.ForeignKey("op_promotions.idop_promotions"), nullable=False)
    promotion_restriction = db.relationship('Promotions', backref=db.backref('op_promotion_restriction', lazy="dynamic"))
    id_restriction = db.Column(db.Integer,db.ForeignKey("def_restriction.iddef_restriction"), nullable=False)
    restriction = db.relationship('Restriction', backref=db.backref('op_promotion_restriction', lazy="dynamic"))
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)


class PromotionRestrictionSchema(ma.Schema):
    idop_promotion_restriction = fields.Integer()
    id_promotion = fields.Integer(required=True)
    id_restriction = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetPromotionRestrictionSchema(ma.Schema):
    idop_promotion_restriction = fields.Integer()
    id_promotion = fields.Integer(required=True)
    id_restriction = fields.Integer(required=True)
    restriction =  ma.Nested("RestrictionSchema",exclude=Util.get_default_excludes())
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
