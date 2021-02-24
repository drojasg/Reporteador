from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate

class PaymentTransactionType(db.Model):
    __tablename__ = "payment_transaction_type"
    
    payment_type = 1
    refund_type = 2
    
    idpayment_transaction_type = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)    
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)


class PaymentTransactionTypeSchema(ma.Schema):
    idpayment_transaction_type = fields.Integer()
    name = fields.String(required=True, validate=validate.Length(max=50))    
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
