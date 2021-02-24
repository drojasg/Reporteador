from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate

class PaymentTransactionDetail(db.Model):
    __tablename__ = "payment_transaction_detail"
    
    idpayment_transaction_detail = db.Column(db.Integer, primary_key=True)
    idpayment_transaction = db.Column(db.Integer, db.ForeignKey('payment_transaction.idpayment_transaction'), nullable=False)
    idFin = db.Column(db.Integer)
    amount = db.Column(db.Float, nullable=False)
    idbook_hotel_room = db.Column(db.Integer, db.ForeignKey('book_hotel_room.idbook_hotel_room'), nullable=False)
    interfaced = db.Column(db.Integer)
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class PaymentTransactionDetailSchema(ma.Schema):
    idpayment_transaction_detail = fields.Integer()
    idpayment_transaction = fields.Integer()
    idFin = fields.Integer()
    amount = fields.Float()
    idbook_hotel_room = fields.Integer()
    interfaced = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
