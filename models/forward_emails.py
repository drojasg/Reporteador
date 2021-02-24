from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from common.util import Util

class ForwardEmails(db.Model):
    __tablename__ = "def_forward_emails"

    iddef_forward_emails = db.Column(db.Integer, primary_key=True)
    idbook_hotel = db.Column(db.Integer, nullable=False)
    reservation = db.Column(db.String(45), nullable=False)
    email = db.Column(db.JSON, nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class ForwardEmailsSchema(ma.Schema):
    iddef_forward_emails = fields.Integer()
    idbook_hotel = fields.Integer()
    reservation = fields.String(validate=validate.Length(max=45))
    email = fields.Dict(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")