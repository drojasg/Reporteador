from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate
#from models.promo_code import PromoCode
#from models.channel import Channel
#from models.promo_code_type_date import PromoCodeTypeDate

class PromoCodeTypeAmount(db.Model):
    __tablename__ = "def_promo_code_type_amount"

    iddef_promo_code_type_amount = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class PromoCodeTypeAmountSchema(ma.Schema):
    iddef_promo_code_type_amount = fields.Integer(dump_only=True)
    name = fields.String(required=True,validate=validate.Length(max=150))
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class PromoCodeTypeAmountRefSchema(ma.Schema):
    iddef_promo_code_type_amount = fields.Integer(dump_only=True)
    name = fields.String(required=True,validate=validate.Length(max=150))
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")