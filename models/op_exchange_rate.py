from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate
from common.base_audit import BaseAudit

class OpExchangeRate(db.Model, BaseAudit):
    __tablename__="op_exchange_rate"
    __table_args__ = {'extend_existing': True}

    idop_exchange_rate = db.Column(db.Integer,primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    currency_code = db.Column(db.String(10), nullable=False, default="")
    amount =  db.Column(db.Float,nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class OpExchangeRateSchema(ma.Schema):
    idop_exchange_rate = fields.Integer(dump_only=True)
    date = fields.DateTime("%Y-%m-%d %H:%M:%S")
    currency_code = fields.String(validate=validate.Length(max=10))
    amount = fields.Float(as_string=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
