from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate
#from models.service import Service

class ServicePrice(db.Model):
    __tablename__ = "def_service_price"
    
    iddef_service_price = db.Column(db.Integer, primary_key=True)
    iddef_service = db.Column(db.Integer, nullable=False)
    #iddef_service = db.Column(db.Integer,db.ForeignKey("def_service.iddef_service"), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    price = db.Column(db.Float, nullable=False)
    min_los = db.Column(db.Integer, nullable=False)
    max_los = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class ServicePriceSchema(ma.Schema):
    iddef_service_price = fields.Integer()
    iddef_service = fields.Integer()
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    price = fields.Float()
    min_los = fields.Integer()
    max_los = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(dump_only=True, required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetServicePriceSchema(ma.Schema):
    iddef_service_price = fields.Integer()
    iddef_service = fields.Integer()
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    price = fields.Float()
    min_los = fields.Integer()
    max_los = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(dump_only=True, required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")