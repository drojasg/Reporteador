from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate
from common.util import Util

class OperaRestrictions(db.Model):
    __tablename__ = "op_opera_restrictions"

    idop_opera_restrictions = db.Column(db.Integer, primary_key=True)
    id_restriction_by = db.Column(db.Integer,nullable=False)
    id_restriction_type = db.Column(db.Integer,nullable=False)
    id_room_type = db.Column(db.Integer,nullable=False)
    id_property = db.Column(db.Integer,nullable=False)
    id_rateplan = db.Column(db.Integer,nullable=False)
    value = db.Column(db.Integer,nullable=False)
    is_override = db.Column(db.Integer,nullable=False)
    date_start = db.Column(db.Date, nullable=False)
    date_end = db.Column(db.Date, nullable=False)
    estado = db.Column()
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)


class OperaRestrictionsSchema(ma.Schema):
    idop_opera_restrictions = fields.Integer(dump_only=True)
    id_restriction_by = fields.Integer(required=True)
    id_restriction_type = fields.Integer(required=True)
    id_room_type = fields.Integer(required=True)
    id_property = fields.Integer(required=True)
    id_rateplan = fields.Integer(required=True)
    value = fields.Integer(required=True)
    is_override = fields.Integer(required=True)
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")


class OperaRestrictionCloseDateSchema(ma.Schema):
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    property = fields.Integer(required=True)
    room = fields.Integer(required=True)
    rateplans = fields.List(fields.Integer())