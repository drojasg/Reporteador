from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate
from models.contact_info_time import ContactInfoTime, ContactInfoTimeSchema
from common.util import Util
from common.base_audit import BaseAudit

class ContactInfo(db.Model, BaseAudit):
    __tablename__ = "def_contact_info"

    iddef_contact_info = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.Integer(), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    agree_terms_conditions = db.Column(db.Integer(), nullable=False, default=0)
    iddef_contact_info_time = db.Column(db.Integer, db.ForeignKey("def_contact_info_time.iddef_contact_info_time"), nullable=False)
    contact_info_time = db.relationship('ContactInfoTime', backref=db.backref('def_contact_info', lazy=True))
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class ContactInfoSchema(ma.Schema):
    iddef_contact_info = fields.Integer()
    name = fields.String(required=True,validate=validate.Length(max=150))
    phone = fields.Integer()
    email = fields.String(validate=validate.Length(max=150))
    agree_terms_conditions = fields.Integer()
    iddef_contact_info_time = fields.Integer()
    contact_info_time = ma.Pluck("ContactInfoTimeSchema", 'description')
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")