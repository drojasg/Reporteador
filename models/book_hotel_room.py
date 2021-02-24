from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from common.util import Util
from sqlalchemy.orm import relationship

from models.pms import Pms
from models.book_pax_room_hotel import BookPaxRoomHotelSchema
from models.book_hotel_room_prices import BookHotelRoomPricesServiceSchema
#from models.book_promotion import BookPromotionSchema
from models.media import publicGetListMedia
from models.book_pax_room_hotel import BookPaxRoomHotelSchema
from models.rates import PricePerDayChangeSchema

class BookHotelRoom(db.Model):
    __tablename__ = "book_hotel_room"
    __table_args__ = {'extend_existing': True}
    pms_opera_default = 1

    charge_option_no_payment = 1
    charge_option_at_moment = 2
    charge_option_before_arrived = 3
    
    amount_to_pay = 0
    amount_to_pending_payment = 0
    charge_option = None

    idbook_hotel_room = db.Column(db.Integer, primary_key=True)
    idbook_hotel = db.Column(db.Integer, db.ForeignKey('book_hotel.idbook_hotel'), nullable=False)
    iddef_room_type = db.Column(db.Integer, db.ForeignKey('def_room_type_category.iddef_room_type_category'), nullable=False)
    idop_rate_plan = db.Column(db.Integer, db.ForeignKey('op_rateplan.idop_rateplan'), nullable=False)
    adults = db.Column(db.Integer, nullable=False, default=0)
    child = db.Column(db.Integer, nullable=False, default=0)
    refundable = db.Column(db.Integer, nullable=False, default=0)
    iddef_police_tax = db.Column(db.Integer, db.ForeignKey('def_policy.iddef_policy'), nullable=False)
    iddef_police_guarantee = db.Column(db.Integer, db.ForeignKey('def_policy.iddef_policy'), nullable=False)
    iddef_police_cancelation = db.Column(db.Integer, db.ForeignKey('def_policy_cancellation_detail.iddef_policy_cancellation_detail'), nullable=False)    
    iddef_pms = db.Column(db.Integer, db.ForeignKey('def_pms.iddef_pms'), nullable=False)    
    pms_confirm_number = db.Column(db.String(100), default="", nullable=False)
    pms_message = db.Column(db.String(100), default="", nullable=False)
    reason_cancellation = db.Column(db.String(200), default="", nullable=False)
    rate_amount = db.Column(db.Float, nullable=False)
    promo_amount = db.Column(db.Float, nullable=False)
    discount_percent = db.Column(db.Float, nullable=False)
    discount_amount = db.Column(db.Float, nullable=False)
    total_gross = db.Column(db.Float, nullable=False)
    country_fee = db.Column(db.Float, nullable=False)
    amount_pending_payment = db.Column(db.Float, nullable=False, default=0)
    amount_paid = db.Column(db.Float, nullable=False, default=0)    
    total = db.Column(db.Float, nullable=False)
    promotion_amount = db.Column(db.Float, nullable=False)
    no_show = db.Column(db.Integer,nullable=False, default=0)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)
    room_type_category = db.relationship('RoomTypeCategory', backref="hotel", lazy=True)
    paxes = db.relationship('BookPaxRoomHotel', backref="room", lazy=True, 
        primaryjoin="and_(BookHotelRoom.idbook_hotel_room == BookPaxRoomHotel.idbook_hotel_room, BookPaxRoomHotel.estado == 1)")
    prices = db.relationship('BookHotelRoomPrices', backref="room", lazy=True, 
        primaryjoin="and_(BookHotelRoom.idbook_hotel_room == BookHotelRoomPrices.idbook_hotel_room, BookHotelRoomPrices.estado == 1)",
        order_by="asc(BookHotelRoomPrices.date)"
    )
    hotelInfo = db.relationship('BookHotel', backref="book_hotel_room", lazy=True)
    #promotions = db.relationship('BookPromotion', backref="room", lazy=True, 
        #primaryjoin="and_(BookHotelRoom.idbook_hotel_room == BookPromotion.idbook_hotel_room, BookPromotion.estado == 1)")
    
class BookHotelRoomSchema(ma.Schema):
    idbook_hotel_room = fields.Integer()
    idbook_hotel = fields.Integer()
    iddef_room_type = fields.Integer()
    idop_rate_plan = fields.Integer()
    adults = fields.Integer()
    child = fields.Integer()
    iddef_police_tax = fields.Integer()
    iddef_police_guarantee = fields.Integer()
    iddef_police_cancelation = fields.Integer()
    pms_confirm_number = fields.String(required=True, validate=validate.Length(max=100))
    pms_message = fields.String(validate=validate.Length(max=100))
    reason_cancellation = fields.String(validate=validate.Length(max=200))
    iddef_pms = fields.Integer()
    rate_amount = fields.Float()
    promo_amount = fields.Float()
    discount_percent = fields.Float()
    discount_amount = fields.Float()
    total_gross = fields.Float()
    country_fee = fields.Float()
    total = fields.Float()
    promotion_amount = fields.Float()
    no_show = fields.Integer()
    #paxes = fields.List(fields.Nested(BookPaxRoomHotelSchema()))    
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class BookModifyRoomSchema(ma.Schema):
    idbook_hotel_room = fields.Integer()
    idbook_hotel = fields.Integer()
    iddef_room_type = fields.Integer()
    idop_rate_plan = fields.Integer()
    iddef_police_tax = fields.Integer()
    iddef_police_guarantee = fields.Integer()
    iddef_police_cancelation = fields.Integer()
    pms_confirm_number = fields.String(required=True, validate=validate.Length(max=100))
    pms_message = fields.String(validate=validate.Length(max=100))
    iddef_pms = fields.Integer()
    rate_amount = fields.Float()
    promo_amount = fields.Float()
    discount_percent = fields.Float()
    discount_amount = fields.Float()
    total_gross = fields.Float()
    country_fee = fields.Float()
    total = fields.Float()
    promotion_amount = fields.Float()
    room_code = fields.String(dump_only=True,attribute="room_type_category.room_code")
    paxes = fields.List(fields.Nested(BookPaxRoomHotelSchema(only=("age_code","iddef_age_range","total","estado"))))
    estado = fields.Integer()
    rates = fields.List(fields.Nested(BookHotelRoomPricesServiceSchema(only=("date","total","price_to_pms"))),attribute="prices")

class BookHotelRoomReservationSchema(ma.Schema):
    idbook_hotel_room = fields.Integer(data_key="room_number")
    idbook_hotel = fields.Integer()
    iddef_room_type = fields.Integer()
    idop_rate_plan = fields.Integer()
    no_show = fields.Integer()
    #iddef_police_tax = fields.Integer()
    #iddef_police_guarantee = fields.Integer()
    #iddef_police_cancelation = fields.Integer()
    pms_confirm_number = fields.String()
    pms_message = fields.String()
    #pms_code = fields.String(required=True, validate=validate.Length(max=50))
    pax = fields.Dict(keys=fields.Str(), values=fields.Integer(), required=True)
    trade_name_room = fields.String(validate=validate.Length(max=1500))
    rateplan_name = fields.String(validate=validate.Length(max=1500))
    prices = fields.List(fields.Nested(BookHotelRoomPricesServiceSchema(only=("date", "price", "total_gross","discount_percent", "discount_amount", "total"))))
    #promotions = fields.List(fields.Nested(BookPromotionSchema(only=("idbook_hotel_room", "idop_promotions", "amount"))))
    media = fields.List(fields.Nested(publicGetListMedia),dump_only=True)
    polices = fields.List(fields.Dict())
    rate_amount = fields.Float()
    promo_amount = fields.Float()
    discount_percent = fields.Float()
    discount_amount = fields.Float()
    total_gross = fields.Float(data_key="total_crossout")
    country_fee = fields.Float()
    total = fields.Float()    
    amount_pending_payment = fields.Float(dump_only=True)
    amount_paid = fields.Float(dump_only=True)
    promotion_amount = fields.Float()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class BookHotelRoomReservationChangeSchema(ma.Schema):
    idbook_hotel_room = fields.Integer(data_key="room_number")
    idbook_hotel = fields.Integer()
    iddef_room_type = fields.Integer()
    idop_rate_plan = fields.Integer()
    pms_confirm_number = fields.String()
    pms_message = fields.String()
    pax = fields.Dict(keys=fields.Str(), values=fields.Integer(), required=True)
    trade_name_room = fields.String(validate=validate.Length(max=1500))
    rateplan_name = fields.String(validate=validate.Length(max=1500))
    prices = fields.List(fields.Nested(BookHotelRoomPricesServiceSchema(only=("date", "price", "total_gross","discount_percent", "discount_amount", "total"))))
    media = fields.List(fields.Nested(publicGetListMedia),dump_only=True)
    polices = fields.List(fields.Dict())
    rate_amount = fields.Float()
    promo_amount = fields.Float()
    discount_percent = fields.Float()
    discount_amount = fields.Float()
    total_gross = fields.Float(data_key="total_crossout")
    country_fee = fields.Float()
    total = fields.Float()
    promotion_amount = fields.Float()
    total_to_paid_room = fields.Float()
    total_room = fields.Float()
    rates = fields.List(fields.Nested(PricePerDayChangeSchema()))
    rates_fix = fields.Boolean()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class BookHotelRoomReservationResponseSchema(BookHotelRoomReservationSchema):    
    pax = fields.Dict(keys=fields.Str(), values=fields.Dict(), required=True)
