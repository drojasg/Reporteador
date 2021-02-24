from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate
from common.base_audit import BaseAudit

class OpContactCustomer(db.Model, BaseAudit):
    __tablename__ = "op_contact_customer"
    #__table_args__={'extended_existing': True}

    idop_contact_customer =  db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(45))
    contact_time = db.Column(db.String(45))
    email = db.Column(db.String(100))
    telephone = db.Column(db.Integer,nullable=False)
    iddef_time_zone = db.Column(db.Integer,nullable=False)
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class OpContactCustomerSchema(ma.Schema):
    idop_contact_customer =fields.Integer(dump_only=True)
    name = fields.String(validate=validate.Length(max=45))
    contact_time = fields.String(validate=validate.Length(max=45))
    email = fields.String(validate=validate.Length(max=45))
    telephone = fields.String(validate=validate.Length(max=15))
    iddef_time_zone =  fields.Integer(default= 0)
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")



