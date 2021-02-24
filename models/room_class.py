from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate
from models.text_lang import TextLang
from common.base_audit import BaseAudit

class RoomClass(db.Model, BaseAudit):
    __tablename__="def_room_class"
    __table_args__ = {'extend_existing': True} 

    iddef_room_class = db.Column(db.Integer,primary_key=True)
    iddef_text_lang = db.Column(db.Integer,db.ForeignKey("def_text_lang.iddef_text_lang"), nullable=False)
    description = db.Column(db.String(45))
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class RoomClassSchema(ma.Schema):
    iddef_room_class = fields.Integer()
    iddef_text_lang = fields.Integer(required=True)
    description = fields.String(required=True,validate=validate.Length(max=45))
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetRoomClassSchema(ma.Schema):
    iddef_room_class = fields.Integer(dump_only=True)
    iddef_text_lang = fields.Integer()
    description = fields.String(required=True,validate=validate.Length(max=45))
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")