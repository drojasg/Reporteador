from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from .address import Address, AddressSchema
from .email_contact import EmailContact, EmailContactSchema
from .contact_phone import ContactPhone, ContactPhoneSchema
from common.util import Util

class Contact(db.Model):
    __tablename__ = "def_contact"

    iddef_contact = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    iddef_contact_type = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)
    addresses = db.relationship('Address', backref=db.backref('contact', lazy=True))
    email_contacts = db.relationship('EmailContact', backref=db.backref('contact', lazy=True))
    contact_phones = db.relationship('ContactPhone', backref=db.backref('contact', lazy=True))

class ContactSchema(ma.Schema):
    iddef_contact = fields.Integer()
    first_name = fields.String(required=True,validate=validate.Length(max=150))
    last_name = fields.String(required=True,validate=validate.Length(max=150))
    iddef_property = fields.Integer()
    iddef_contact_type = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    addresses = fields.Nested(AddressSchema, many=True, exclude=Util.get_default_excludes())
    email_contacts = fields.Nested(EmailContactSchema, many=True, exclude=Util.get_default_excludes())
    contact_phones = fields.Nested(ContactPhoneSchema, many=True, exclude=Util.get_default_excludes())

class ContactPostSchema(ma.Schema):
    iddef_contact = fields.Integer()
    first_name = fields.String(required=True,validate=validate.Length(max=150))
    last_name = fields.String(required=True,validate=validate.Length(max=150))
    iddef_contact_type = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    addresses = fields.Nested(AddressSchema, many=True, exclude=Util.get_default_excludes())
    email_contacts = fields.Nested(EmailContactSchema, many=True, exclude=Util.get_default_excludes())
    contact_phones = fields.Nested(ContactPhoneSchema, many=True, exclude=Util.get_default_excludes())
    iddef_property = fields.Integer()