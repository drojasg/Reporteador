from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from common.util import Util

class BookExtraType(db.Model):
    __tablename__ = "book_extra_type"

    default_service_booking_engine = 1

    idbook_extra_type = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45),nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class BookExtraTypeSchema(ma.Schema):

    idbook_extr_type = fields.Integer(dump_only=True)
    name = fields.String(validate=validate.Length(max=45))
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")