from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from common.util import Util

class BookHotelComment(db.Model):
    __tablename__ = "book_hotel_comment"
    source_public = 1  # => public
    source_admin = 2  # => admin booking engine    
    
    idbook_hotel_comment = db.Column(db.Integer, primary_key=True)
    idbook_hotel = db.Column(db.Integer, db.ForeignKey('book_hotel.idbook_hotel'), nullable=False)
    text = db.Column(db.String(250), nullable=False)
    visible_to_guest = db.Column(db.Integer, nullable=False)
    source = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)


class BookHotelCommentSchema(ma.Schema):
    class Meta:
        ordered = True
        
    idbook_hotel_comment = fields.Integer()
    idbook_hotel = fields.Integer()
    text = fields.String(required=True, validate=validate.Length(max=250))
    visible_to_guest = fields.Integer()
    source = fields.Integer()
    source_text = fields.Method("get_source_text")
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

    def get_source_text(self, obj):
        if obj.source == 1:
            return "public"
        else:
            return "admin"
    
class BookHotelCommentUpdateSchema(ma.Schema):
    class Meta:
        ordered = True

    idbook_hotel_comment = fields.Integer()
    idbook_hotel = fields.Integer()
    text = fields.String(required=True, validate=validate.Length(max=250))
    visible_to_guest = fields.Boolean()
    source = fields.Integer()
    source_text = fields.Method("get_source_text")
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

    def get_source_text(self, obj):
        if obj.source == 1:
            return "public"
        else:
            return "admin"