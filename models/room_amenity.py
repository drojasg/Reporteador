from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate
from models.amenity import Amenity, AmenitySchema, GetListAmenitySchema
from models.room_type_category import RoomTypeCategory, RoomTypeCategorySchema
from models.amenity_group import AmenityGroup, AmenityGroupSchema

class RoomAmenity(db.Model):
    __tablename__="def_room_amenity"
    __table_args__ = {'extend_existing': True}

    iddef_room_amenity = db.Column(db.Integer,primary_key=True)
    iddef_amenity = db.Column(db.Integer,db.ForeignKey("def_amenity.iddef_amenity"), nullable=False)
    amenity = db.relationship('Amenity', backref=db.backref('def_room_amenity', lazy="dynamic"))
    iddef_room_type_category = db.Column(db.Integer, db.ForeignKey("def_room_type_category.iddef_room_type_category"),nullable=False)
    room = db.relationship('RoomTypeCategory', backref=db.backref('def_room_amenity', lazy="dynamic"))
    is_priority = db.Column(db.Integer)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)


class RoomAmenitySchema(ma.Schema):
    iddef_room_amenity = fields.Integer()
    iddef_amenity = fields.Integer(required=True)
    iddef_room_type_category = fields.Integer(required=True)
    is_priority = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(
        required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetRoomAmenitySchema(ma.Schema):
    iddef_room_amenity = fields.Integer(dump_only=True)
    iddef_amenity = fields.Integer()
    iddef_room_type_category = fields.Integer()
    is_priority = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True,validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetRoomAmenityDumpSchema(ma.Schema):
    iddef_room_amenity = fields.Integer()
    iddef_amenity = fields.Integer()
    iddef_room_type_category = fields.Integer()
    amenity_info = fields.Nested(Amenity)
    amenity_name = fields.String(attribute='amenity_info.html_icon')

class RoomAmenityDescription(ma.Schema):
    iddef_amenity = fields.Integer()
    html_icon = fields.String()
    text = fields.String()
    is_priority = fields.Integer()
    attribute = fields.String(validate=validate.Length(max=100))
    
