from datetime import datetime
from sqlalchemy.sql.expression import and_
from config import db, ma
from marshmallow import Schema, fields, validate
from .policy import Policy, PolicySchema
from common.util import Util
from models.book_hotel import BookHotel
from models.book_customer import BookCustomerReservationSchema
from models.book_hotel_room import BookHotelRoomReservationSchema

class PruebaBookingSchema(ma.Schema):
    idbook_hotel = fields.Integer(dump_only = True)
    code_reservation = fields.String(required = True, validate = validate.Length(max = 60))
    iddef_property = fields.Integer()
    from_date = fields.DateTime("%Y-%m-%d %H:%M:%S")
    to_date = fields.DateTime("%Y-%m-%d %H:%M:%S")
    nights = fields.Integer()
    adults = fields.Integer()
    child = fields.Integer()
    total_rooms = fields.Integer()
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
    Hotel_Name = fields.String(attribute =  "tr_name", dump_only = True)
    Property_Code = fields.String(attribute = "pr_code", dump_only = True)
    Currency_Code = fields.String(attribute = "ms_code", dump_only = True)
    Market_Description = fields.String(attribute = "ms_description")
    Country_name = fields.String(attribute = "co_name", dump_only = True)
    Country_Code = fields.String(attribute = "co_code", dump_only = True)
    BookStatus_ID = fields.String(attribute = "bs_idBookStatus", dumps_only = True)
    BookStatus_Name = fields.String(attribute = "bs_name", dump_only = True)
    BookStatus_Code = fields.String(attribute = "bs_code", dump_only = True)
    BookStatus_Description = fields.String(attribute = "bs_description", dump_only = True)
    email = fields.String(attribute = "guest_email", dump_only = True)
    expiry_date = fields.DateTime("%Y-%m-%d %H:%M:%S")
    cancelation_date = fields.DateTime("%Y-%m-%d %H:%M:%S")
    modification_date_booking = fields.DateTime("%Y-%m-%d %H:%M:%S")
    estado = fields.Integer()
    usuario_creacion = fields.String(required = True, validate = validate.Length(max = 45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required = True, validate = validate.Length(max = 45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    guest_name = fields.String()
    guest_phone = fields.String()
    room_type = fields.String()
    rooms = fields.List(fields.Nested(BookHotelRoomReservationSchema(only=("idbook_hotel_room", "iddef_room_type", "idop_rate_plan", "pax",\
        "trade_name_room", "prices", "discount_percent", "discount_amount", "total_gross", "total", "media", "rateplan_name", "promo_amount"))))

# class PruebaBookingSchemav2(ma.Schema):
