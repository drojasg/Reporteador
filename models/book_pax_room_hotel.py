from config import db, ma
from enum import Enum
from marshmallow import Schema, fields, validate
from datetime import datetime
from common.util import Util

class BookPaxRoomHotel(db.Model):
    __tablename__ = "book_pax_room_hotel"

    idbook_pax_room_hotel = db.Column(db.Integer, primary_key=True)
    iddef_age_range = db.Column(db.Integer, db.ForeignKey('def_age_range.iddef_age_range'), nullable=False)
    age_code = db.Column(db.String(25), nullable=False)
    idbook_hotel_room = db.Column(db.Integer, db.ForeignKey('book_hotel_room.idbook_hotel_room'), nullable=False)
    total = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class BookPaxRoomHotelSchema(ma.Schema):
    idbook_pax_room_hotel = fields.Integer()
    iddef_age_range = fields.Integer()
    age_code = fields.String(required=True, validate=validate.Length(max=25))
    idbook_hotel_room = fields.Integer()
    total = fields.Integer()
    date = fields.DateTime("%Y-%m-%d")
    price = fields.Float()
    discount_amount = fields.Float()
    total = fields.Float()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
