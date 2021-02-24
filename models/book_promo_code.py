from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from common.util import Util

class BookPromoCode(db.Model):
    __tablename__ = "book_promo_code"
    __table_args__ = {'extend_existing': True}
    
    idbook_promo_code = db.Column(db.Integer, primary_key=True)
    is_text = db.Column(db.Integer, nullable=False)
    promo_code_type = db.Column(db.Integer,nullable=False)
    promo_code = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    idbook_hotel = db.Column(db.Integer, db.ForeignKey('book_hotel.idbook_hotel'), nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)


class BookPromoCodeSchema(ma.Schema):
    idbook_promo_code = fields.Integer()
    is_text = fields.Integer()
    promo_code = fields.String(required=True, validate=validate.Length(max=50))
    amount = fields.Float()
    idbook_hotel = fields.Integer()
    estado = fields.Integer()    
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
