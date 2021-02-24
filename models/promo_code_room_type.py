from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate
from models.promo_code import PromoCode
from models.room_type_category import RoomTypeCategory
from common.base_audit import BaseAudit

class PromoCodeRoomType(db.Model, BaseAudit):
    __tablename__ = "def_promo_code_room_type"

    iddef_promo_code_room_type = db.Column(db.Integer, primary_key=True)
    iddef_promo_code = db.Column(db.Integer, db.ForeignKey("def_promo_code.iddef_promo_code"), nullable=False)
    iddef_room_type_category = db.Column(db.Integer, db.ForeignKey("def_room_type_category.iddef_room_type_category"), nullable=False)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class PromoCodeRoomTypeTypeSchema(ma.Schema):
    iddef_promo_code_room_type = fields.Integer(dump_only=True)
    iddef_promo_code = fields.Integer(dump_only=True)
    iddef_room_type_category = fields.Integer(dump_only=True) 
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class PromoCodeRoomTypeTypeRefSchema(ma.Schema):
    iddef_promo_code_room_type = fields.Integer(dump_only=True)
    iddef_promo_code = fields.Integer(dump_only=True)
    iddef_room_type_category = fields.Integer(dump_only=True) 
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
