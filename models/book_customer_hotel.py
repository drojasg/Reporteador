from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from common.util import Util

class BookCustomerHotel(db.Model):
    __tablename__ = "book_customer_hotel"

    idbook_customer_hotel = db.Column(db.Integer, primary_key=True)
    idbook_hotel = db.Column(db.Integer, db.ForeignKey('book_hotel.idbook_hotel'), nullable=False)    
    idbook_customer = db.Column(db.Integer, db.ForeignKey('book_customer.idbook_customer'), nullable=False)
    is_holder = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)
    customer = db.relationship("BookCustomer", uselist=False, lazy="joined")

class BookCustomerHotelSchema(ma.Schema):    
    idbook_customer_hotel = fields.Integer()
    idbook_hotel = fields.Integer()
    idbook_customer = fields.Integer()
    is_holder = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(
        validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
