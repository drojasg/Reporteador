from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime

class EmailContact(db.Model):
    __tablename__ = "def_email_contact"

    iddef_email_contact = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), nullable=False)
    notify_booking = db.Column(db.Integer, nullable=False)
    iddef_contact = db.Column(db.Integer, db.ForeignKey("def_contact.iddef_contact"), nullable=False)
    email_type = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class EmailContactSchema(ma.Schema):
    iddef_email_contact = fields.Integer()
    email = fields.String(validate=validate.Length(max=150))
    notify_booking = fields.Integer()
    iddef_contact = fields.Integer()
    email_type = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")