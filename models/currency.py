from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate

class Currency(db.Model):
    __tablename__ = "def_currency"
    __table_args__ = {'extend_existing': True}
    
    iddef_currency = db.Column(db.Integer, primary_key=True)
    currency_code = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    own_exchange_rate = db.Column(db.Float, nullable=False)
    estado = db.Column(db.Integer, nullable=False, default=1)
    usuario_creacion = db.Column(db.String, nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.now)
    usuario_ultima_modificacion = db.Column(db.String, nullable=False, default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, nullable=False, default="1900-01-01 00:00:00", onupdate = datetime.now)

class CurrencySchema(ma.Schema):
    iddef_currency = fields.Integer(dump_only=True)
    currency_code = fields.String(required=True,validate=validate.Length(max=10))
    description = fields.String(validate=validate.Length(max=60))
    own_exchange_rate = fields.Float()
    estado = fields.Integer(load_only=False)
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetCurrencySchema(ma.Schema):
    iddef_currency = fields.Integer()
    currency_code = fields.String(required=True,validate=validate.Length(max=10))
    description = fields.String(validate=validate.Length(max=60))
    own_exchange_rate = fields.Float()
    estado = fields.Integer(load_only=True)

class CurrencyUpdateSchema(ma.Schema):
    iddef_currency = fields.Integer()
    currency_code = fields.String(required=False,validate=validate.Length(max=10))
    description = fields.String(validate=validate.Length(max=60))
    own_exchange_rate = fields.Float()
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
