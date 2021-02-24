from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate
from models.description_type import DescriptionType, DescriptionTypeSchema
from models.property import Property, PropertySchema

class PropertyDescription(db.Model):
    __tablename__="def_property_description"
    __table_args__ = {'extend_existing': True} 

    iddef_property_description = db.Column(db.Integer,primary_key=True)
    iddef_description_type = db.Column(db.Integer,db.ForeignKey("def_description_type.iddef_description_type"), nullable=False)
    iddef_property = db.Column(db.Integer, db.ForeignKey("def_property.iddef_property"), nullable=False)
    lang_code = db.Column(db.String(10),nullable=False)
    title = db.Column(db.String(200))
    description = db.Column(db.String(3000))
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class PropertyDescriptionSchema(ma.Schema):
    iddef_property_description = fields.Integer(dump_only=True)
    iddef_description_type = fields.Integer(required=True)
    iddef_property = fields.Integer(required=True)
    #iddef_property = fields.Nested(PropertySchema,only=['property_code'])
    #iddef_property = fields.Pluck(PropertySchema,'property_code')
    lang_code = fields.String(required=True,validate=validate.Length(max=10))
    title = fields.String(required=True,validate=validate.Length(max=200))
    description = fields.String(required=True,validate=validate.Length(max=3000))
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class PropertyDescriptionRefSchema(ma.Schema):
    iddef_property_description = fields.Integer(required=True)
    iddef_description_type = fields.Integer(required=True)
    iddef_property = fields.Integer(required=True)
    #iddef_property = fields.Nested(PropertySchema,only=['property_code'])
    #iddef_property = fields.Pluck(PropertySchema,'property_code')
    lang_code = fields.String(required=True,validate=validate.Length(max=10))
    title = fields.String(required=True,validate=validate.Length(max=200))
    description = fields.String(required=True,validate=validate.Length(max=3000))
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class DumpPropertyDescriptionSchema(ma.Schema):
    iddef_property_description = fields.Integer(dump_only=True)
    iddef_description_type = fields.Integer(required=True,load_only=True)
    iddef_property = fields.Integer(required=True,load_only=True)
    lang_code = fields.String(required=True,validate=validate.Length(max=10),load_only=True)
    title = fields.String(required=True,validate=validate.Length(max=200))
    description = fields.String(required=True,validate=validate.Length(max=3000))
    estado = fields.Integer(load_only=True)
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")