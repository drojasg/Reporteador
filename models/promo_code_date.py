from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate
#from models.promo_code import PromoCode
from models.channel import Channel
from models.promo_code_type_date import PromoCodeTypeDate

class PromoCodeDate(db.Model):
    __tablename__ = "def_promo_code_date"

    iddef_promo_code_date = db.Column(db.Integer, primary_key=True)
    iddef_promo_code = db.Column(db.Integer, db.ForeignKey("def_promo_code.iddef_promo_code"), nullable=False)
    iddef_promo_code_type_date =db.Column(db.Integer, db.ForeignKey("def_promo_code_type_date.iddef_promo_code_type_date"), nullable=False)
    start_date = db.Column(db.DateTime, default="1900-01-01 00:00:00", nullable=False)
    end_date = db.Column(db.DateTime, default="1900-01-01 00:00:00", nullable=False)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)
    promo_code = db.relationship('PromoCode', backref=db.backref('def_promo_code', lazy='dynamic'))

class PromoCodeDateSchema(ma.Schema):

    iddef_promo_code_date = fields.Integer(dump_only=True)
    iddef_promo_code = fields.Integer(dump_only=True)
    iddef_promo_code_type_date = fields.Integer(dump_only=True)
    start_date = fields.DateTime("%Y-%m-%d %H:%M:%S")
    end_date = fields.DateTime("%Y-%m-%d %H:%M:%S")
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    promo_code = ma.Pluck("PromoCodeSchema", 'iddef_promo_code')

class PromoCodeDateRefSchema(ma.Schema):

    iddef_promo_code_date = fields.Integer(dump_only=True)
    iddef_promo_code = fields.Integer(dump_only=True)
    iddef_promo_code_type_date = fields.Integer(dump_only=True)
    start_date = fields.DateTime("%Y-%m-%d %H:%M:%S")
    end_date = fields.DateTime("%Y-%m-%d %H:%M:%S")
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class PromoCodeDateInsertSchema(ma.Schema):
    iddef_promo_code_date = fields.Integer()
    iddef_promo_code = fields.Integer()
    iddef_promo_code_type_date = fields.Integer()
    start_date = fields.DateTime("%Y-%m-%d %H:%M:%S")
    end_date = fields.DateTime("%Y-%m-%d %H:%M:%S")
    estado = fields.Integer()