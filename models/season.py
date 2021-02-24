from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate
from models.property import Property
from common.base_audit import BaseAudit

class Season(db.Model, BaseAudit):
    __tablename__ = "def_season"

    iddef_season = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(150), nullable=False)
    iddef_property = db.Column(db.Integer, db.ForeignKey("def_property.iddef_property"), nullable=False)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class SeasonSchema(ma.Schema):
    iddef_season = fields.Integer(dump_only=True)
    description = fields.String(required=True, validate=validate.Length(max=150))
    iddef_property = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class SeasonRefSchema(ma.Schema):
    iddef_season = fields.Integer(dump_only=True)
    description = fields.String(required=True, validate=validate.Length(max=150))
    iddef_property = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
