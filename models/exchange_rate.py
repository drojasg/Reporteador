from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate

class ExchangeRate(db.Model):
    __tablename__ = "op_exchange_rate"
    default_currency_code = "USD"

    idop_exchange_rate = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    currency_code = db.Column(db.String(10), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)


class ExchangeRateSchema(ma.Schema):
    idop_exchange_rate = fields.Integer()    
    date = fields.DateTime("%Y-%m-%d")
    currency_code = fields.String(required=True, validate=validate.Length(max=10))
    amount = fields.Float()    
    estado = fields.Integer()
    usuario_creacion = fields.String(
        required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(
        validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
