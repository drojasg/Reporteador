from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate
from models.market_segment import MarketSegment, MarketSegmentSchema

class Country(db.Model):
    __tablename__ = "def_country"
    __table_args__ = {'extend_existing': True}
    
    iddef_country = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    country_code = db.Column(db.String, nullable=False)
    alias = db.Column(db.String, nullable=False)
    idmarket_segment = db.Column(db.Integer,db.ForeignKey("def_market_segment.iddef_market_segment"), nullable=False)
    market = db.relationship('MarketSegment', backref=db.backref('def_country', lazy='dynamic'))
    dialling_code = db.Column(db.String, nullable=False, default="")
    estado = db.Column(db.Integer, nullable=False, default=1)
    usuario_creacion = db.Column(db.String, nullable=False)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.now)
    usuario_ultima_modificacion = db.Column(db.String, nullable=False, default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, nullable=False, default="1900-01-01 00:00:00", onupdate = datetime.now)

class CountrySchema(ma.Schema):
    iddef_country = fields.Integer(dump_only=True)
    name = fields.String(required=True,validate=validate.Length(max=45))
    country_code = fields.String(required=True,validate=validate.Length(max=45))
    alias = fields.String(required=True,validate=validate.Length(max=45))
    idmarket_segment = fields.Integer(required=True)
    market = ma.Pluck("MarketSegmentSchema", 'code')
    dialling_code = fields.String(required=True,validate=validate.Length(max=20))
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class SaveCountrySchema(ma.Schema):
    iddef_country = fields.Integer(dump_only=True)
    name = fields.String(required=True,validate=validate.Length(max=45))
    country_code = fields.String(required=True,validate=validate.Length(max=45))
    alias = fields.String(required=True,validate=validate.Length(max=45))
    idmarket_segment = fields.Integer(required=True)
    dialling_code = fields.String(required=True,validate=validate.Length(max=20))
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    data_langs = fields.List(fields.Dict(),required=True)