from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate
from models.restriction import Restriction
from models.service import Service
from common.util import Util

class ServiceRestriction(db.Model):
    __tablename__ = "def_service_restriction"

    iddef_service_restriction = db.Column(db.Integer, primary_key=True)
    iddef_restriction = db.Column(db.Integer,db.ForeignKey("def_restriction.iddef_restriction"), nullable=False)
    service_restriction = db.relationship('Restriction', backref=db.backref('def_service_restriction', lazy="dynamic"))
    iddef_service = db.Column(db.Integer,db.ForeignKey("def_service.iddef_service"), nullable=False)
    service = db.relationship('Service', backref=db.backref('def_service_restriction', lazy="dynamic"))
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)


class ServicerestrictionSchema(ma.Schema):
    iddef_service_restriction = fields.Integer()
    iddef_restriction = fields.Integer(required=True)
    iddef_service = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    service_restriction =  ma.Nested("RestrictionSchema",exclude=Util.get_default_excludes())