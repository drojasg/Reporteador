from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate
from models.segment import Segment
from models.property_type import PropertyType
from models.brand import Brand
from models.area_unit import AreaUnit, AreaUnitSchema
from models.property_category import PropertyCategory
from models.zones import Zones
from models.time_zone import TimeZone, TimeZoneSchema
from models.media import publicGetListMedia
from models.amenity import publicAmenities
from .contact import Contact, ContactSchema
from .policy import Policy, PolicySchema
from common.util import Util

book_hotel_properties = db.Table('book_hotel',
    db.column('iddef_property', db.Integer, db.ForeignKey('def_property.iddef_property'),primary_key = True),
    db.column('iddef_market_segment', db.Integer, db.ForeignKey('def_market_segment.iddef_market_segment'), primary_key = True),
    db.column('iddef_country', db.Integer, db.ForeignKey('def_country.iddef_country'), primary_key = True),
    db.column('iddef_channel', db.Integer, db.ForeignKey('def_channel.iddef_channel') primary_key = True),
    db.column('iddef_currency', db.Integer, db.ForeignKey('def_currency.iddef_currency') primary_key = True),
    db.column('iddef_language', db.Integer, db.ForeignKey('def_language.iddef_language') primary_key = True),
    db.column('idbook_status', db.Integer, db.ForeignKey('book_status.idbook_status' primary_key = True))
)

class PruebaBooking(db.Model):
    __tablename__ = "book_hotel"

    idbook_hotel = db.Column(db.Integer, primary_key = True)
    code_reservation = db.Column(db.String(60), nullable = False)
    iddef_property = db.Column(db.Integer, db.ForeignKey("def_property.iddef_property"), nullable = False)
    short_name = db.Column(db.String(45), nullable = False)
    trade_name = db.Colum(db.String(45), nullable = False)
    property_code = db.Column(db.String(6), nullable = False)
    from_date = db.Column(db.DateTime)
    to_date = db.Column(db.DateTime)
    nights = db.Column(db.Integer)
    adults = db.Column(db.Integer)
    currency_code = db.Column(db.String(15), nullable = False)
    description = db.Column(db.String(100), nullable = False)
    iddef_country = db.Column(db.Integer, db.ForeignKey("def_country.iddef_country"), nullable = False)
    name = db.Colum(db.String(45), nullable = False)
    country_code = db.Column(db.String(45), nullable = False)
    iddef_channel = db.Column(db.Integer, db.ForeignKey("def_channel.iddef_channel"), nullable = False)
    name = db.Column(db.String(150), nullable = False)
    iddef_currency = db.Column(db.Integer, db.ForeignKey("def_currency.iddef_currency"), nullable = False)
    currency_code = db.Column(db.String(15), nullable = False)
    description = db.Column(db.Strin(60), nullable = False)
    iddef_language = db.Column(db.Integer, db.ForeignKey("def_language.iddef_language"), nullable = False)
    lang_code = db.Colum(db.String(10), nullable = False)
    description = db.Column(db.String(60), nullable = False)
    exchange_rate = db.Column(db.Float, nullable = False)
    promo_amount = db.Column(db.Float, nullable = False)
    discount_percent = db.Column(db.Float, nullable = False)
    discount_amount = db.Column(db.FLoat, nullable = False)
    total_gross = db.Column(db.Float, nullable = False)
    fee_amount = db.Column(db.Float, nullable = False)
    country_fee = db.Column(db.Float, nullable = False)
    amount_pending_payment = db.Column(db.Float, nullable = False)
    amount_paid = db.Column(db.Float, nullable = False)
    total = db.Column(db.Float, nullable = False)
    promotion_amount = db.Column(db.Float, nullable = False)
    last_refund_amount = db.Column(db.Float, nullable = False)
    idbook_status = db.Column(db.Integer, db.ForeignKey("book_status.idbook_status"), nullable = False)
    name = db.Column(db.String(50), nullable = False)
    code = db.Column(db.String(50), nullable = False)
    description = db.Column(db.String(100), nullable = False)
    device_request = db.Column(db.String(50), nullable = False)
    expiry_date = db.Column(db.DateTime, nullable = False)
    cancelation_date = db.Column(db.DateTime, nullable = False)
    modification_date_booking = db.Column(db.DateTime, nullable = False)
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable = False)
    fecha_creacion = db.Column(db.DateTime)
    usuario_ultima_modificacion = db.Column(db.String)
    fecha_ultima_modificacion = db.Column(db.DateTime)

class PruebaBookingSchema(ma.Schema):
    idbook_hotel = fields.Integer()
    code_reservation = fields.String(required = True, validate = validate.Length(max = 60))
    iddef_property = fields.Integer()
    short_name = fields.String(required = True, validate = validate.Length(max = 45))
    trade_name = fields.String(required = True, validate = validate.Length(max = 45))
    property_code = fields.String(required = True, validate = validate.Length(max = 6))
    from_date = fields.DateTime("%Y-%m-%d %H:%M:%S")
    to_date = fields.DateTime("%Y-%m-%d %H:%M:%S")
    nights = fields.Integer()
    adults = fields.Integer()
    currency_code = fields.String(required = True, validate = validate.Length(max = 15))
    description = fields.String(required = True, validate = validate.Length(max = 100))
    iddef_country = fields.Integer()
    name = fields.String(required = True, validate = validate.Length(max = 45))
    country_code =  fields.String(required = True, validate = validate.Length(max = 45))
    iddef_channel = fields.Integer()
    name = fields.String(required = True, validate = validate.Length(max = 150))
    iddef_currency = fields.Integer()
    currency_code = fields.String(required = True, validate = validate.Length(max = 15))
    descripton = fields.Strimg(required = True, validate = validate.Length(max = 60 ))
    iddef_language = fields.Integer()
    lang_code = fields.String(required = True, validate = validate.Length(max = 10))
    description = fields.String(required = True, validate = validate.Length(max = 60))
    exchange_rate = fields.Float()
    promo_amount = fields.Float()
    discount_percent = fields.Float()
    discount_amount = fields.Float()
    total_gross = fields.Float()
    fee_amount = fields.Float()
    country_fee = fields.Float()
    amount_pending_payment = fields.Float()
    amount_paid = fields.Float()
    total = fields.Float()
    promotion_amount = fields.Float()
    last_refund_amount = fields.Float()
    idbook_status = fields.Integer()
    name = fields.String(required = True, valdiate = validate.Length(max = 50))
    code = fields.String(required = True, validate = validate.Length(max = 50))
    description = fields.String(required = True, valdiate = validate.Length(max = 100))
    device_request = fields.String(required = True, validate = validate.Length(max = 50))
    expiry_date = fields.DateTime("%Y-%m-%d %H:%M:%S")
    cancelation_date = fields.DateTime("%Y-%m-%d %H:%M:%S")
    modification_date_booking = fields.DateTime("%Y-%m-%d %H:%M:%S")
    estado = fields.Integer()
    usuario_creacion = fields.Strig(required = True, validate = validate.Length(max = 45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.DAteTime("%Y-%m-%d %H:%M:%S")
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
