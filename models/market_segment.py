from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate

class MarketSegment(db.Model):
    __tablename__ = "def_market_segment"

    iddef_market_segment = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(15), nullable=False)
    currency_code = db.Column(db.String(15), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    pms_profile_id = db.Column(db.String(100), nullable=False, default="")
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)


class MarketSegmentSchema(ma.Schema):
    iddef_market_segment = fields.Integer()
    code = fields.String(
        required=True, validate=validate.Length(max=15))
    currency_code = fields.String(
        required=True, validate=validate.Length(max=15))
    description = fields.String(
        required=True, validate=validate.Length(max=100))
    pms_profile_id= fields.String(
        required=True, validate=validate.Length(max=100)
    )
    estado = fields.Integer()
    usuario_creacion = fields.String(
        required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")