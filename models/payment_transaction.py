from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate

class PaymentTransaction(db.Model):
    __tablename__ = "payment_transaction"
    
    idpayment_transaction = db.Column(db.Integer, primary_key=True)
    idbook_hotel = db.Column(db.Integer, db.ForeignKey('book_hotel.idbook_hotel'), nullable=False)
    idpayment_method = db.Column(db.Integer, db.ForeignKey('payment_method.idpayment_method'), nullable=False)
    idpayment_transaction_type = db.Column(db.Integer, db.ForeignKey('payment_transaction_type.idpayment_transaction_type'), nullable=False)
    card_code = db.Column(db.String(50), nullable=False)
    authorization_code = db.Column(db.Integer)
    merchant_code = db.Column(db.String(50), nullable=False)
    ticket_code = db.Column(db.Integer)
    idfin_payment = db.Column(db.Integer)
    amount = db.Column(db.Float, nullable=False)
    exchange_rate = db.Column(db.Float, nullable=False)
    currency_code = db.Column(db.String(10), nullable=False)
    idop_sistema = db.Column(db.Integer, default=0)
    external_code = db.Column(db.String(10), nullable=False, default="")
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)
    details = db.relationship('PaymentTransactionDetail', backref="payment", lazy="joined",
        primaryjoin="and_(PaymentTransaction.idpayment_transaction == PaymentTransactionDetail.idpayment_transaction, PaymentTransactionDetail.estado == 1)")
    payment_method = db.relationship('PaymentMethod', backref="payment", lazy=True)
    payment_type = db.relationship('PaymentTransactionType', backref="payment", lazy=True)

class PaymentSchema(ma.Schema):
    idpayment_transaction = fields.Integer()
    idbook_hotel = fields.Integer()
    idpayment_method = fields.Integer()
    idpayment_transaction_type = fields.Integer()
    card_code = fields.String(validate=validate.Length(max=50))
    authorization_code = fields.Integer()
    merchant_code = fields.String(validate=validate.Length(max=50))
    ticket_code = fields.Integer()
    idfin_payment = fields.Integer()
    amount = fields.Float()
    exchange_rate = fields.Float()
    currency_code = fields.String(validate=validate.Length(max=10))
    transaction_type = fields.String(validate=validate.Length(max=50))
    payment_method = fields.String(validate=validate.Length(max=50))
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")


class PaymentReservationSchema(ma.Schema):
    card_number = fields.String(validate=validate.Length(min=1, max=20, error='Field cannot be blank'), required=True, load_only=True)
    holder_first_name = fields.String(validate=validate.Length(min=1, max=100, error='Field cannot be blank'), required=True)
    holder_last_name = fields.String(validate=validate.Length(min=1, max=100, error='Field cannot be blank'), required=True)
    exp_month = fields.Integer(required=True, load_only=True)
    exp_year = fields.Integer(required=True, load_only=True)
    cvv = fields.String(required=True, load_only=True)
    card_type = fields.String(dump_only=True)

class CardSchema(ma.Schema):
    card_number = fields.String(required=True)
    exp_month = fields.Integer(required=True)
    exp_year = fields.Integer(required=True)
    cvv = fields.Integer(required=True)
    #id_hotel = fields.Integer(required=True)
    holder_first_name = fields.String(required=True)
    holder_last_name = fields.String(required=True)
