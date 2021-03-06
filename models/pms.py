from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate

class Pms(db.Model):
    __tablename__ = "def_pms"
    __table_args__ = {'extend_existing': True}

    iddef_pms = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(100), nullable=False)    
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class PmsSchema(ma.Schema):
    iddef_pms = fields.Integer()
    code = fields.String(required=True, validate=validate.Length(max=50))
    name = fields.String(required=True, validate=validate.Length(max=50))
    description = fields.String(required=True, validate=validate.Length(max=100))
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
