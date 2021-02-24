from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate
from models.brand import Brand

class TermsAndConditions(db.Model):
    __tablename__ = "def_terms_and_conditions"

    iddef_terms_and_conditions = db.Column(db.Integer, primary_key=True)
    link_es = db.Column(db.String(500), nullable=False)
    link_en = db.Column(db.String(500), nullable=False)
    iddef_brand = db.Column(db.Integer, db.ForeignKey("def_brand.iddef_brand"), nullable=False)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class TermsAndConditionsSchema(ma.Schema):
    iddef_terms_and_conditions = fields.Integer(dump_only=True)
    link_es = fields.String(required=True,validate=validate.Length(max=500))
    link_en = fields.String(required=True,validate=validate.Length(max=500))
    iddef_brand = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class TermsAndConditionsRefSchema(ma.Schema):
    iddef_terms_and_conditions = fields.Integer(dump_only=True)
    link_es = fields.String(required=True,validate=validate.Length(max=500))
    link_en = fields.String(required=True,validate=validate.Length(max=500))
    iddef_brand = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")