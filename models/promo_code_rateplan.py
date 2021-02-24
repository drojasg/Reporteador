from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate
from models.property import Property
from models.rateplan import RatePlan, RatePlanIdSchema
from common.util import Util

# promo_code_rateplans = db.Table('def_promo_code_rateplan',
#     db.Column('iddef_promo_code', db.Integer, db.ForeignKey('def_promo_code.iddef_promo_code'), primary_key=True),
#     db.Column('idop_rateplan', db.Integer, db.ForeignKey('op_rateplan.idop_rateplan'), primary_key=True)
# )

class PromoCodeRatePlan(db.Model):
    __tablename__ = "def_promo_code_rateplan"

    iddef_promo_code_rateplan = db.Column(db.Integer, primary_key=True)
    iddef_promo_code = db.Column(db.Integer, db.ForeignKey("def_promo_code.iddef_promo_code"), nullable=False)
    iddef_property = db.Column(db.Integer, db.ForeignKey("def_property.iddef_property"), nullable=False)
    idop_rateplan = db.Column(db.Integer, db.ForeignKey("op_rateplan.idop_rateplan"), nullable=False)
    op_rateplans = db.relationship('RatePlan', backref=db.backref('def_promo_code_rateplan', lazy=True))
    rooms_rateplan = db.Column(db.JSON, nullable=False, default={})
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class PromoCodeRatePlanSchema(ma.Schema):
    iddef_promo_code_rateplan = fields.Integer()
    iddef_promo_code = fields.Integer()
    iddef_property = fields.Integer()
    idop_rateplan = fields.Integer()
    op_rateplans = fields.Nested(RatePlanIdSchema, exclude=Util.get_default_excludes())
    rooms_rateplan = fields.List(fields.String())
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")