from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate
#from models.description_type import DescriptionType, DescriptionTypeSchema

class TextLang(db.Model):
    __tablename__="def_text_lang"

    iddef_text_lang = db.Column(db.Integer,primary_key=True)
    lang_code = db.Column(db.String(10),nullable=False)
    text = db.Column(db.Text,nullable=False)
    table_name = db.Column(db.String,nullable=False)
    id_relation = db.Column(db.Integer,nullable=False)
    attribute = db.Column(db.String(100))
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class TextLangSchema(ma.Schema):
    iddef_text_lang = fields.Integer()
    lang_code = fields.String(validate=validate.Length(max=10))
    text = fields.String(required=True)
    table_name = fields.String(validate=validate.Length(max=150))
    id_relation = fields.Integer()
    attribute = fields.String(validate=validate.Length(max=100))
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetTextLangSchema(ma.Schema):
    lang_code = fields.String(validate=validate.Length(max=10),required=True)
    text = fields.String(required=True)
    estado = fields.Integer()

class PostPutTextLangSchema(ma.Schema):
    lang_code = fields.String(validate=validate.Length(max=10))
    text = fields.String(required=True)
    estado = fields.Integer()
    iddef_text_lang = fields.Integer()
    attribute = fields.String(validate=validate.Length(max=100))
    
class PutTextLangSchema(ma.Schema):
    iddef_text_lang = fields.Integer()
    lang_code = fields.String(required=True, validate=validate.Length(max=10))
    text = fields.String(required=True)
    table_name = fields.String(validate=validate.Length(max=150))
    id_relation = fields.Integer()
    attribute = fields.String(validate=validate.Length(max=100))
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")