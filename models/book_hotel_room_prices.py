from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from common.util import Util

class BookHotelRoomPrices(db.Model):
    __tablename__ = "book_hotel_room_prices"

    idbook_hotel_room_prices = db.Column(db.Integer, primary_key=True)
    idbook_hotel_room = db.Column(db.Integer, db.ForeignKey('book_hotel_room.idbook_hotel_room'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Float, nullable=False)
    price_to_pms = db.Column(db.Float, nullable=False)
    promo_amount = db.Column(db.Float, nullable=False)
    discount_percent = db.Column(db.Float, nullable=False)
    discount_amount = db.Column(db.Float, nullable=False)
    total_gross = db.Column(db.Float, nullable=False)
    country_fee = db.Column(db.Float, nullable=False)
    amount_pending_payment = db.Column(db.Float, nullable=False, default=0)
    amount_paid = db.Column(db.Float, nullable=False, default=0)
    total = db.Column(db.Float, nullable=False)
    promotion_amount = db.Column(db.Float, nullable=False)
    code_promotions = db.Column(db.String(45), nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class BookHotelRoomPricesSchema(ma.Schema):
    idbook_hotel_room_prices = fields.Integer()
    idbook_hotel_room = fields.Integer()
    date = fields.DateTime("%Y-%m-%d")
    price = fields.Float()
    promo_amount = fields.Float()
    discount_percent = fields.Float()
    discount_amount = fields.Float()
    total_gross = fields.Float()
    country_fee = fields.Float()
    total = fields.Float()
    promotion_amount = fields.Float()
    code_promotions = fields.String(validate=validate.Length(max=45))
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class BookHotelRoomPricesServiceSchema(ma.Schema):
    idbook_hotel_room_prices = fields.Integer()
    idbook_hotel_room = fields.Integer()
    date = fields.DateTime("%Y-%m-%d")
    price = fields.Float()
    promo_amount = fields.Float()
    discount_percent = fields.Float()
    discount_amount = fields.Float()
    total_gross = fields.Float()
    country_fee = fields.Float()
    total = fields.Float()
    price_to_pms = fields.Float()
    promotion_amount = fields.Float()
    code_promotions = fields.String(validate=validate.Length(max=45))
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
