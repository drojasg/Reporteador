from datetime import datetime
from config import db, ma
from models.languaje import Languaje
from models.property import Property
from marshmallow import Schema, fields, validate

class PropertyLang(db.Model):
    __tablename__ = "def_property_lang"

    iddef_property_lang = db.Column(db.Integer, primary_key=True)
    iddef_property = db.Column(db.Integer,db.ForeignKey("def_property.iddef_property"), nullable=False)
    property = db.relationship('Property', backref=db.backref('def_property_lang', lazy="dynamic"))
    iddef_language = db.Column(db.Integer,db.ForeignKey("def_language.iddef_language"), nullable=False)
    language = db.relationship('Languaje', backref=db.backref('def_property_lang', lazy="dynamic"))
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)


class PropertyLangSchema(ma.Schema):
    iddef_property_lang = fields.Integer(dump_only=True)
    iddef_property = fields.Integer(required=True)
    iddef_language = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetPropertyLangSchema(ma.Schema):
    iddef_property_lang = fields.Integer(dump_only=True)
    iddef_property = fields.Integer(load_only=True)
    property = ma.Pluck("PropertySchema", 'property_code')
    iddef_language = fields.Integer(load_only=True)
    language = ma.Pluck("LanguajeSchema", 'description')
    language_code = fields.String(attribute='language.lang_code')
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetDumpPropertyLangSchema(ma.Schema):
    iddef_property_lang = fields.Integer(dump_only=True)
    iddef_property = fields.Integer()
    property = ma.Pluck("PropertySchema", 'property_code')
    iddef_language = fields.Integer(load_only=True)
    language = ma.Pluck("LanguajeSchema", 'description')
    language_code = fields.String(attribute='language.lang_code')
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")