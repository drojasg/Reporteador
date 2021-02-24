from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate

class PropertyCategory(db.Model):
    __tablename__ = "def_property_category"
    
    iddef_property_category = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String, nullable=False)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.now)
    usuario_ultima_modificacion = db.Column(db.String, nullable=False)
    fecha_ultima_modificacion = db.Column(db.DateTime, nullable=False, default="1900-01-01 00:00:00", onupdate = datetime.now)   

class PropertyCategorySchema(ma.Schema):
    iddef_property_category = fields.Integer()
    name = fields.String(required=True, validate=validate.Length(max=50))
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
