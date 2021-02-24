from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from models.auth_item import AuthItem

class AuthAssignment(db.Model):
    __tablename__ = "auth_assignment"

    item_name = db.Column(db.String(64), db.ForeignKey('auth_item.name'), primary_key=True)
    credentials_id = db.Column(db.Integer, db.ForeignKey('def_credentials.iddef_credentials'), nullable=False, primary_key=True)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class AuthAssignmentSchema(ma.Schema):
    item_name = fields.String(required=True, validate=validate.Length(max=64))
    credentials_id = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")