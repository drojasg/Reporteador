from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate
from models.property import Property
from models.price_type import PriceType
from models.text_lang import TextLang, GetTextLangSchema
from models.age_code import AgeCode, AgeCodeSchema
from common.util import Util

class AgeRange(db.Model):
    __tablename__ = "def_age_range"

    iddef_age_range = db.Column(db.Integer, primary_key=True)
    iddef_property = db.Column(db.Integer,db.ForeignKey("def_property.iddef_property"), nullable=False)
    age_range_property = db.relationship('Property', backref=db.backref('def_age_range', lazy='dynamic'))
    #iddef_default_price_type = db.Column(db.Integer,db.ForeignKey("def_default_price_type.iddef_default_price_type"), nullable=False)
    #age_range_price_type = db.relationship('PriceType', backref=db.backref('def_age_range', lazy='dynamic'))
    #age_from = db.Column(db.Integer)
    #age_to = db.Column(db.Integer)
    #default_price_value = db.Column(db.Integer)
    iddef_age_code = db.Column(db.Integer,db.ForeignKey("def_age_code.iddef_age_code"), nullable=False)
    age_range_age_code = db.relationship('AgeCode', backref=db.backref('def_age_range', lazy='dynamic'))
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class AgeRangeSchema(ma.Schema):
    iddef_age_range = fields.Integer()
    iddef_property = fields.Integer(required=True)
    #iddef_default_price_type = fields.Integer(required=True)
    #age_from = fields.Integer()
    #age_to = fields.Integer()
    #default_price_value = fields.Integer()
    iddef_age_code = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(
        required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetAgeRangeSchema(ma.Schema):
    iddef_age_range = fields.Integer()
    iddef_property = fields.Integer()
    #iddef_default_price_type = fields.Integer()
    #age_from = fields.Integer()
    #age_to = fields.Integer()
    #default_price_value = fields.Integer()
    iddef_age_code = fields.Integer()
    age_range_age_code = fields.Nested(AgeCodeSchema, exclude=Util.get_default_excludes())
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetAgeRangeListSchema(ma.Schema):
    iddef_age_range = fields.Integer()
    age_from = fields.Integer()
    age_to = fields.Integer()
    age_range_age_code = fields.Nested(AgeCodeSchema, exclude=Util.get_default_excludes())
    estado = fields.Integer(load_only=True)

class SaveAgeRangeSchema(ma.Schema):
    iddef_age_range = fields.Integer()
    iddef_property = fields.Integer(required=True)
    #iddef_default_price_type = fields.Integer()
    #age_from = fields.Integer(required=True)
    #age_to = fields.Integer(required=True)
    #default_price_value = fields.Integer()
    iddef_age_code = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    datos = fields.Nested(GetTextLangSchema, many=True)

class UpdateAgeRangeSchema(ma.Schema):
    iddef_age_code = fields.Integer()
    code = fields.String(validate=validate.Length(max=25))
    disable_edit = fields.Integer()
    age_from = fields.Integer()
    age_to = fields.Integer()    
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    appliedproperties = fields.List(fields.Integer(),required=True)
    nameGroup = fields.List(fields.Dict(),required=True)

class GetListAgeRangeSchema(ma.Schema):
    iddef_age_range = fields.Integer()
    age_range_property = ma.Pluck("PropertySchema", 'property_code')
    #age_range_price_type = ma.Pluck("PriceTypeSchema", 'description')
    age_range_age_code = ma.Pluck("AgeCodeSchema", 'code')
    #age_from = fields.Integer()
    #age_to = fields.Integer()
    #default_price_value = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
class age_code(ma.Schema):
    age_max = fields.Integer()
    age_min = fields.Integer()
    code = fields.String()
    description = fields.String()
    #text = fields.Dict(fields.String(),fields.String())

class age_range(ma.Schema):
    fields.Dict(fields.String(),fields.Nested(age_code))
    