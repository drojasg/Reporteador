from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate

class PromoCodeTypeDate(db.Model):
    __tablename__ = "def_promo_code_type_date"

    iddef_promo_code_type_date = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class PromoCodeTypeDateSchema(ma.Schema):
    iddef_promo_code_type_date = fields.Integer(dump_only=True)
    name = fields.String(required=True,validate=validate.Length(max=150))
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class PromoCodeTypeDateRefSchema(ma.Schema):
    iddef_promo_code_type_date = fields.Integer(dump_only=True)
    name = fields.String(required=True,validate=validate.Length(max=150))
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")