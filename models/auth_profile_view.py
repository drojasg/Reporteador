from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from common.util import Util

class AuthProfileView(db.Model):
    __tablename__ = "auth_profile_view"
    __table_args__ = (
        db.UniqueConstraint("auth_item", "controller", "action", name='unique_auth_profile'),
    )

    id_profile_view = db.Column(db.Integer, primary_key=True)
    auth_item = db.Column(db.String(64), db.ForeignKey('auth_item.name'))
    controller = db.Column(db.String(64), nullable=False)
    action = db.Column(db.String(64), nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class AuthProfileViewSchema(ma.Schema):
    id_profile_view = fields.Integer()
    auth_item = fields.String(required=True, validate=validate.Length(max=64))
    controller = fields.String(required=True, validate=validate.Length(max=64))
    action = fields.String(required=True, validate=validate.Length(max=64))
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")