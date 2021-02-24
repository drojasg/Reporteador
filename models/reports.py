from config import db, ma
from marshmallow import Schema, fields, validate
from common.base_audit import BaseAudit
from datetime import datetime
from common.util import Util

class Reports(db.Model, BaseAudit):
    __tablename__ = "reports"

    idreports = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(150), nullable=False)
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class ReportsSchema(ma.Schema):    
    idreports = fields.Integer()
    name = fields.String(required=True,validate=validate.Length(max=100))
    description = fields.String(required=True,validate=validate.Length(max=150))   
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class DailySalesSchema(ma.Schema):
    iddef_market_segment = fields.Integer(dump_only=True, required=False)
    code = fields.String(dump_only=True, required=False)
    total_booking_value = fields.String(dump_only=True, required=False)
    bookings =  fields.Decimal(dump_only=True, as_string=True, places=2)
    total_room_nights = fields.Decimal(dump_only=True, as_string=True, places=2)
    avg_daily_rate = fields.Decimal(dump_only=True, as_string=True, places=2)
    avg_los = fields.Decimal(dump_only=True, as_string=True, places=2)

class DailySalesDetailedSchema(ma.Schema):
    iddef_property = fields.Integer(dump_only=True)
    code = fields.String(dump_only=True)
    property_code = fields.String(dump_only=True, required=False)
    trade_name = fields.String(dump_only=True)
    channel_name = fields.String(dump_only=True)
    total_booking_value = fields.String(dump_only=True, required=False)
    bookings =  fields.Decimal(dump_only=True, as_string=True, places=2)
    total_room_nights = fields.Decimal(dump_only=True, as_string=True, places=2)
    avg_daily_rate = fields.Decimal(dump_only=True, as_string=True, places=2)
    avg_los = fields.Decimal(dump_only=True, as_string=True, places=2)
    iddef_market_segment = fields.Integer(dump_only=True, required=False)

class DailyCancelationConsolidatedSchema(ma.Schema):
    idbook_hotel = fields.Integer(dump_only=True)
    property_code = fields.String(dump_only=True, required=False)
    code = fields.String(dump_only=True, required=False)
    total_booking_value = fields.String(dump_only=True)
    bookings =  fields.Integer(dump_only=True)
    total_room_nights = fields.Integer(dump_only=True)
    avg_daily_rate = fields.String(dump_only=True)
    avg_los = fields.Integer(dump_only=True)
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    cancelation_date = fields.DateTime("%Y-%m-%d %H:%M:%S")

class ConsolidatedSalesByRoomCategorySchema(ma.Schema):
    code = fields.String(dump_only=True, required=False)
    property_code = fields.String(dump_only=True, required=False)
    room_code = fields.String(dump_only=True)
    reserved = fields.Integer(dump_only=True)
    canceled = fields.Integer(dump_only=True)
    bookings = fields.Integer(dump_only=True)
    total_room_nights = fields.Integer(dump_only=True)
    cancelation_rate = fields.String(dump_only=True)
    avg_daily_rate = fields.Decimal(dump_only=True, as_string=True, places=2)
    avg_los = fields.Decimal(dump_only=True, as_string=True, places=2)


class DailyReservationsListSchema(ma.Schema):
    property_code = fields.String(dump_only=True, required=False)
    currency_code = fields.String(dump_only=True)
    device_request = fields.String(dump_only=True)
    country_name = fields.String(dump_only=True)
    country_ID = fields.String(dump_only=True)
    modified_date = fields.DateTime("%Y-%m-%d %H:%M:%S")
    total_guest = fields.Integer(dump_only=True)
    book_status = fields.String(dump_only=True)
    user_device = fields.String(dump_only=True)
    cancelation_date = fields.String(dump_only=True)
    booking_date = fields.DateTime("%Y-%m-%d %H:%M:%S")
    month = fields.String(dump_only=True)
    time = fields.String(dump_only=True)
    code_reservation = fields.String(dump_only=True)
    guest_name = fields.String(dump_only=True)
    guest_city = fields.String(dump_only=True)
    guest_state = fields.String(dump_only=True)
    arrival_date = fields.DateTime("%Y-%m-%d")
    departure_date = fields.DateTime("%Y-%m-%d")
    bookings = fields.Integer(dump_only=True)
    room_code = fields.String(dump_only=True)
    room_name = fields.String(dump_only=True)
    adults = fields.Integer(dump_only=True)
    child = fields.Integer(dump_only=True)
    rateplan_name = fields.String(dump_only=True)
    rate_code = fields.String(dump_only=True)
    total_room_nights = fields.String(dump_only=True)
    rate_amount = fields.Decimal(dump_only=True, as_string=True, places=3)
    promo_code = fields.String(dump_only=True)
    promo_code_amount = fields.Integer(dump_only=True)
    total_room_value  = fields.Decimal(dump_only=True, as_string=True, places=3)
    avg_daily_rate = fields.Decimal(dump_only=True, as_string=True, places=3)
    avg_los = fields.Decimal(dump_only=True, as_string=True, places=3)
    user_market = fields.String(dump_only=True)
    dailing_code = fields.String(dump_only=True)
    guest_phone = fields.String(dump_only=True)
    guest_email = fields.String(dump_only=True)
    channel= fields.String(dump_only=True)
    services = fields.String(dump_only=True)
    is_repetitive_customer = fields.String(dump_only=True)
    reason_cancellation= fields.String(dump_only=True)


class BookingOnHoldConsolidated(ma.Schema):
    code = fields.String(dump_only=True)
    property_code = fields.String(dump_only=True)
    bookings_onhold = fields.Integer(dump_only=True)
    total_booking_convert = fields.Integer(dump_only=True)
    convert_rate = fields.String(dump_only=True)
    total_room_nights = fields.Integer(dump_only=True)
    bookings = fields.Integer(dump_only=True)
    avg_daily_rate = fields.String(dump_only=True)
    #fields.Decimal(dump_only=True, as_string=True, places=3)
    total_booking_value = fields.String(dump_only=True, required=False)
    avg_los = fields.Decimal(dump_only=True, as_string=True, places=3)

class PromotionConsolidated(ma.Schema):
    code = fields.String(dump_only=True)
    property_code = fields.String(dump_only=True)
    promo_code_name = fields.String(dump_only=True)
    promo_code = fields.String(dump_only=True)
    promo_code_type = fields.String(dump_only=True)
    bookings = fields.Integer(dump_only=True)
    total_room_nights = fields.Integer(dump_only=True)
    avg_daily_rate = fields.String(dump_only=True)
    avg_los = fields.Integer(dump_only=True)
    total_booking_value = fields.String(dump_only=True)

class ConsolidatedDailySales(ma.Schema):
    hotel_name = fields.String(dump_only=True)
    total_booking_value = fields.String(dump_only=True)
    bookings = fields.Integer(dump_only=True)
    total_room_nights = fields.Integer(dump_only=True)
    avg_daily_rate = fields.String(dump_only=True)
    avg_los = fields.Decimal(dump_only=True, as_string=True, places=3)

class GeneralConsolidatedDailySales(ma.Schema):
    bookings = fields.Integer(dump_only=True)
    total_room_nights = fields.Integer(dump_only=True)
    average_daily_rate_on_total_room = fields.Decimal(dump_only=True, as_string=True, places=3)
    avg_los = fields.Decimal(dump_only=True, as_string=True, places=3)
    total_booking_value = fields.Decimal(dump_only=True, as_string=True, places=3)