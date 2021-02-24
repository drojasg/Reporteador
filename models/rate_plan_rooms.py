from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate
from models.room_type_category import RoomTypeCategory, RoomTypeCategorySchema
from common.util import Util

class RatePlanRooms(db.Model):
    __tablename__="op_rate_plan_rooms"
    __table_args__ = {'extend_existing': True} 

    idop_rate_plan_rooms = db.Column(db.Integer,primary_key=True)
    id_rate_plan = db.Column(db.Integer,db.ForeignKey("op_rateplan.idop_rateplan"), nullable=False)
    id_room_type = db.Column(db.Integer,db.ForeignKey("def_room_type_category.iddef_room_type_category"), nullable=False)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)
    rooms = db.relationship('RoomTypeCategory', backref=db.backref('op_rate_plan_rooms', lazy=True))

class RatePlanRoomsSchema(ma.Schema):
    idop_rate_plan_rooms = fields.Integer()
    id_rate_plan = fields.Integer(required=True)
    id_room_type = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    rooms = fields.Nested("RoomTypeCategorySchema", many=False, exclude=Util.get_default_excludes())