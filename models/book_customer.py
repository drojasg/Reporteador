from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from common.util import Util
from models.book_address import BookAddressSchema
from sqlalchemy.orm import relationship

class BookCustomer(db.Model):
    __tablename__ = "book_customer"

    idbook_customer = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(10), nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    dialling_code = db.Column(db.String(45), nullable=False)
    phone_number = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    birthdate = db.Column(db.Date, nullable=False)
    company = db.Column(db.String(150), nullable=False)
    id_profile = db.Column(db.String(50), default="")
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)
    address = db.relationship("BookAddress", uselist=False, back_populates="customer", lazy="joined")



class BookCustomerSchema(ma.Schema):
    idbook_customer = fields.Integer()
    title = fields.String(required=True, validate=validate.Length(max=10))
    first_name = fields.String(
        required=True, validate=validate.Length(max=150))
    last_name = fields.String(required=True, validate=validate.Length(max=150))
    phone_number = fields.String(
        required=True, validate=validate.Length(max=50))
    email = fields.String(required=True, validate=validate.Length(max=150))
    birthdate = fields.DateTime("%Y-%m-%d")
    company = fields.String(required=True, validate=validate.Length(max=150))
    id_profile = fields.String(
        required=False, validate=validate.Length(max=50))
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(
        validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class BookCustomerModifySchema(ma.Schema):
    idbook_customer = fields.Integer()
    title = fields.String(required=True, validate=validate.Length(max=10))
    first_name = fields.String(
        required=True, validate=validate.Length(max=150))
    last_name = fields.String(required=True, validate=validate.Length(max=150))
    phone_number = fields.String(
        required=True, validate=validate.Length(max=50))
    email = fields.String(required=True, validate=validate.Length(max=150))
    birthdate = fields.DateTime("%Y-%m-%d")
    company = fields.String(required=True, validate=validate.Length(max=150))
    id_profile = fields.String(
        required=False, validate=validate.Length(max=50))
    dialling_code = fields.String()
    estado = fields.Integer()
    idbook_address = fields.Integer(attribute="address.idbook_address")
    #idbook_customer = fields.Integer()
    city = fields.String(attribute="address.city")
    country_code = fields.String(attribute="address.country_code")    
    address = fields.String(attribute="address.address")
    street = fields.String(attribute="address.street")
    state = fields.String(attribute="address.state")
    zip_code = fields.String(attribute="address.zip_code")
    address_estado = fields.Integer(attribute="address.estado")

class BookCustomerReservationSchema(ma.Schema):
    idbook_customer = fields.Integer()
    title = fields.String(required=True, validate=validate.Length(max=10))
    first_name = fields.String(
        required=True, validate=validate.Length(max=150))
    last_name = fields.String(required=True, validate=validate.Length(max=150))
    dialling_code = fields.String(required=True, validate=validate.Length(max=45))
    phone_number = fields.String(
        required=True, validate=validate.Length(max=50))
    email = fields.String(required=True, validate=validate.Length(max=150))
    birthdate = fields.DateTime("%Y-%m-%d")
    company = fields.String(required=True, validate=validate.Length(max=150))
    id_profile = fields.String(
        required=False, validate=validate.Length(max=50))
    address = fields.Nested(BookAddressSchema, required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(
        validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
