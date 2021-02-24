from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from common.base_audit import BaseAudit

class TranslationMessage(db.Model, BaseAudit):
    __tablename__ = "def_translation_message"

    iddef_translation_message = db.Column(db.Integer, primary_key=True)
    lang_code = db.Column(db.String(10), nullable=False)
    key = db.Column(db.String(255), nullable=False)
    text = db.Column(db.String(2000), nullable=False)
    page = db.Column(db.String(50), nullable=False)
    allow_public = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class TranslationMessageSchema(ma.Schema):

    page = TranslationMessage.page
    iddef_translation_message= fields.Integer()
    lang_code = fields.String(required=True, validate=validate.Length(max=10))
    key = fields.String(required=True, validate=validate.Length(max=255))
    text = fields.String(required=True, validate=validate.Length(max=255))
    page = fields.String(required=False, validate=validate.Length(max=50))
    allow_public = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
