from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from common.util import Util
from sqlalchemy.orm import relationship

class BookAddress(db.Model):
    __tablename__ = "book_address"

    idbook_address = db.Column(db.Integer, primary_key=True)
    idbook_customer = db.Column(db.Integer, db.ForeignKey('book_customer.idbook_customer'), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    iddef_country = db.Column(db.Integer, db.ForeignKey('def_country.iddef_country'), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    street = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)
    customer = db.relationship("BookCustomer", back_populates="address")
    country = db.relationship('Country', backref="hotel", lazy="joined")

class BookAddressSchema(ma.Schema):    
    idbook_address = fields.Integer()
    idbook_customer = fields.Integer()
    city = fields.String(required=True, validate=validate.Length(max=50))
    country_code = fields.String(required=True, validate=validate.Length(max=2))    
    address = fields.String(required=True, validate=validate.Length(max=200))
    street = fields.String(required=True, validate=validate.Length(max=100))
    state = fields.String(required=True, validate=validate.Length(max=100))
    zip_code = fields.String(required=True, validate=validate.Length(max=50))
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
