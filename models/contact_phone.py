from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime

class ContactPhone(db.Model):
    __tablename__ = "def_contact_phone"

    iddef_contact_phone = db.Column(db.Integer, primary_key=True)
    iddef_phone_type = db.Column(db.Integer, nullable=False)
    iddef_contact = db.Column(db.Integer, db.ForeignKey("def_contact.iddef_contact"), nullable=False)
    country = db.Column(db.String(45), nullable=False)
    area = db.Column(db.String(45), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    extension = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion =  db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion =  db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class ContactPhoneSchema(ma.Schema):
    iddef_contact_phone = fields.Integer()
    iddef_phone_type = fields.Integer(required=True)
    iddef_contact = fields.Integer(required=True)
    country = fields.String(validate=validate.Length(max=45))
    area = fields.String(validate=validate.Length(max=45))
    number = fields.Integer()
    extension = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")