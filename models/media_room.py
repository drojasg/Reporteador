from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate
from models.media import Media
from models.room_type_category import RoomTypeCategory
#from models.service import Service
from common.util import Util

class MediaRoom(db.Model):
    __tablename__ = "def_media_room"
    __table_args__ = {'extend_existing': True}

    iddef_media_room = db.Column(db.Integer,primary_key=True)
    iddef_media = db.Column(db.Integer,db.ForeignKey("def_media"), nullable=False)
    iddef_room_type_category = db.Column(db.Integer,db.ForeignKey("def_room_type_category"), nullable = False)
    order = db.Column(db.Integer,nullable=False)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class MediaRoomSchema(ma.Schema):
    iddef_media_room = fields.Integer()
    iddef_media = fields.Integer(required=True)
    iddef_room_type_category = fields.Integer(required=True)
    order = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetMediaRoomAdminSchema(ma.Schema):
    iddef_media_room = fields.Integer()
    iddef_media = fields.Integer()
    name = fields.String(validate=validate.Length(max=100))
    description = fields.String(validate=validate.Length(max=150))
    url = fields.String(validate=validate.Length(max=100))
    selected = fields.Integer()
    order = fields.Integer()
    iddef_media_type = fields.Integer()
    tags = fields.Dict()
    etag = fields.String(required=True,validate=validate.Length(max=255))
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class PostMediaRoomSchema(ma.Schema):
    iddef_room_type_category = fields.Integer()
    order = fields.Integer()
    medias_id = fields.List(fields.Dict())
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class UpdateOrderSchema(ma.Schema):
    iddef_media_room = fields.Integer()
    order = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")