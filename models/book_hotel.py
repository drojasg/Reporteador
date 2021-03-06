from config import db, ma
from marshmallow import Schema, fields, validate, validates_schema, ValidationError, pre_dump
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta

from common.util import Util
from models.book_customer import BookCustomerReservationSchema
from models.book_hotel_room import BookHotelRoomReservationSchema, BookHotelRoomReservationResponseSchema, BookHotelRoomReservationChangeSchema
from models.book_promotion import BookPromotionSchema
from models.property import PropertyBookSchema
from models.book_extra_service import BookExtraServiceReservationSchema
from models.media import publicGetListMedia
from models.payment_transaction import PaymentReservationSchema
from models.book_hotel_comment import BookHotelCommentSchema, BookHotelCommentUpdateSchema

class BookHotel(db.Model):
    __tablename__ = "book_hotel"
    __table_args__ = {'extend_existing': True}

    lang_code = None
    amount_to_pay = 0
    
    idbook_hotel = db.Column(db.Integer, primary_key=True)    
    iddef_property = db.Column(db.Integer, db.ForeignKey('def_property.iddef_property'),nullable=False)
    code_reservation = db.Column(db.String(60), nullable=False)
    from_date = db.Column(db.Date, nullable=False)
    to_date = db.Column(db.Date, nullable=False)
    nights = db.Column(db.Integer, nullable=False)
    adults = db.Column(db.Integer, nullable=False)
    child = db.Column(db.Integer, nullable=False)
    total_rooms = db.Column(db.Integer, nullable=False)
    iddef_market_segment = db.Column(db.Integer, db.ForeignKey('def_market_segment.iddef_market_segment'), nullable=False)
    iddef_country = db.Column(db.Integer, db.ForeignKey('def_country.iddef_country'), nullable=False)
    iddef_language = db.Column(db.Integer, db.ForeignKey('def_language.iddef_language'), nullable=False)
    iddef_currency = db.Column(db.Integer, db.ForeignKey('def_currency.iddef_currency'), nullable=False)
    iddef_currency_user = db.Column(db.Integer, db.ForeignKey('def_currency.iddef_currency'), nullable=False)
    iddef_channel = db.Column(db.Integer, db.ForeignKey('def_channel.iddef_channel'), nullable=False)
    exchange_rate = db.Column(db.Float, nullable=False)
    promo_amount = db.Column(db.Float, nullable=False)
    discount_percent = db.Column(db.Float, nullable=False)
    discount_amount = db.Column(db.Float, nullable=False)
    total_gross = db.Column(db.Float, nullable=False)
    fee_amount = db.Column(db.Float, nullable=False)
    country_fee = db.Column(db.Float, nullable=False)
    amount_pending_payment = db.Column(db.Float, nullable=False, default=0)
    amount_paid = db.Column(db.Float, nullable=False, default=0)
    total = db.Column(db.Float, nullable=False)
    promotion_amount = db.Column(db.Float, nullable=False)
    last_refund_amount = db.Column(db.Float, nullable=False, default=0)
    idbook_status = db.Column(db.Integer, db.ForeignKey('book_status.idbook_status'), nullable=False)
    device_request = db.Column(db.String(50), nullable=False, default="desktop")
    expiry_date = db.Column(db.DateTime, default="1900-01-01 00:00:00")
    cancelation_date = db.Column(db.DateTime, default="1900-01-01 00:00:00")
    #visible_reason_cancellation = db.Column(db.Integer, default=0)
    modification_date_booking = db.Column(db.DateTime, default="1900-01-01 00:00:00")
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)    
    property = db.relationship('Property', backref="hotel", lazy="select")
    customers = db.relationship('BookCustomerHotel', backref="hotel", lazy="select")
    comments = db.relationship('BookHotelComment', backref="hotel", lazy="select",
        primaryjoin="and_(BookHotel.idbook_hotel == BookHotelComment.idbook_hotel, BookHotelComment.estado == 1)")
    promo_codes = db.relationship('BookPromoCode', backref="hotel", lazy="select")
    market_segment = db.relationship('MarketSegment', backref="hotel", lazy="select")
    country = db.relationship('Country', backref="hotel_country", lazy="select")
    language = db.relationship('Languaje', backref="hotel", lazy="select")
    currency = db.relationship('Currency', backref="hotel", lazy="select", foreign_keys=[iddef_currency])
    currency_user = db.relationship('Currency', backref="hotel_user", lazy="select", foreign_keys=[iddef_currency_user])
    channel = db.relationship('Channel', backref="hotel_channel", lazy="select")
    status_item = db.relationship('BookStatus', backref="hotel", lazy="select")
    rooms = db.relationship('BookHotelRoom', backref="hotel", lazy="select",
        primaryjoin="and_(BookHotel.idbook_hotel == BookHotelRoom.idbook_hotel, BookHotelRoom.estado == 1)")
    services = db.relationship('BookExtraService', backref="hotel", lazy="select",
        primaryjoin="and_(BookHotel.idbook_hotel == BookExtraService.idbook_hotel, BookExtraService.estado == 1)")
    payments = db.relationship('PaymentTransaction', backref="hotel", lazy="select",
        primaryjoin="and_(BookHotel.idbook_hotel == PaymentTransaction.idbook_hotel, PaymentTransaction.estado != 0)")
    # promotions = db.relationship('BookPromotion', backref="hotel", lazy="select", 
    #     primaryjoin="and_(BookHotel.idbook_hotel == BookPromotion.idbook_hotel, BookPromotion.estado == 1)")

class BookHotelSchema(ma.Schema):
    idbook_hotel = fields.Integer()        
    iddef_property = fields.Integer()
    code_reservation = fields.String(validate=validate.Length(max=60))
    from_date = fields.DateTime("%Y-%m-%d")
    to_date = fields.DateTime("%Y-%m-%d")
    nights = fields.Integer()
    adults = fields.Integer()
    child = fields.Integer()
    total_rooms = fields.Integer()
    iddef_market_segment = fields.Integer()
    iddef_country = fields.Integer()
    iddef_language = fields.Integer()
    iddef_channel = fields.Integer()
    iddef_currency = fields.Integer()
    iddef_currency_user = fields.Integer()
    exchange_rate = fields.Float()
    promo_amount = fields.Float()
    discount_percent = fields.Float()
    discount_amount = fields.Float()
    total_gross = fields.Float()
    fee_amount = fields.Float()
    country_fee = fields.Float()
    total = fields.Float()
    promotion_amount = fields.Float()
    idbook_status = fields.Integer()
    expiry_date = fields.DateTime("%Y-%m-%d")
    cancelation_date = fields.DateTime("%Y-%m-%d")
    visible_reason_cancellation = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class BookHotelBaseSchema(ma.Schema):
    idbook_hotel = fields.Integer()
    code_reservation = fields.String(validate=validate.Length(max=60))        
    iddef_property = fields.Integer()
    property_code = fields.String(validate=validate.Length(max=6))
    from_date = fields.DateTime("%Y-%m-%d")
    to_date = fields.DateTime("%Y-%m-%d")
    nights = fields.Integer()
    adults = fields.Integer()
    child = fields.Integer()
    total_rooms = fields.Integer()
    iddef_market_segment = fields.Integer()
    market_code = fields.String(validate=validate.Length(max=15))
    iddef_country = fields.Integer()
    country_code = fields.String(validate=validate.Length(max=45))
    iddef_language = fields.Integer()
    lang_code = fields.String(validate=validate.Length(max=10))
    iddef_channel = fields.Integer()
    iddef_currency = fields.Integer()
    currency_code = fields.String(validate=validate.Length(max=10))
    iddef_currency_user = fields.Integer()
    currency_code_user = fields.String(validate=validate.Length(max=10))
    exchange_rate = fields.Float()
    promo_amount = fields.Float()
    discount_percent = fields.Float()
    discount_amount = fields.Float()
    total_gross = fields.Float()
    fee_amount = fields.Float()
    country_fee = fields.Float()
    total = fields.Float()
    promotion_amount = fields.Float()
    idbook_status = fields.Integer()
    expiry_date = fields.DateTime("%Y-%m-%d")
    cancelation_date = fields.DateTime("%Y-%m-%d")
    visible_reason_cancellation = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class BookHotelReservationSchema(ma.Schema):
    idbook_hotel = fields.Integer()
    idbook_customer = fields.Integer()
    #iddef_property = fields.Integer(required=True)
    iddef_brand = fields.Integer()
    property_code = fields.String(required=True, validate=validate.Length(max=6))
    from_date = fields.DateTime("%Y-%m-%d")
    to_date = fields.DateTime("%Y-%m-%d")
    nights = fields.Integer()
    total_rooms = fields.Integer()
    market_code = fields.String(required=True, validate=validate.Length(max=10))
    iddef_channel = fields.Integer(required=True)
    lang_code = fields.String(required=True, validate=validate.Length(max=10))
    currency_code = fields.String(required=True, validate=validate.Length(max=10))
    promo_code = fields.String(validate=validate.Length(max=50))
    special_request = fields.String(validate=validate.Length(max=250))
    on_hold = fields.Boolean(required=True)
    customer = fields.Nested(BookCustomerReservationSchema(only=("title", "first_name", "last_name", "dialling_code", "phone_number", "email", "birthdate", "company", "address")), required=True)
    rooms = fields.List(fields.Nested(BookHotelRoomReservationSchema(only=("idbook_hotel_room", "iddef_room_type", "idop_rate_plan", "pax",\
        "trade_name_room", "prices", "discount_percent", "discount_amount", "total_gross", "total", "media", "rateplan_name", "promo_amount"))))
    services_info = fields.List(fields.Nested(BookExtraServiceReservationSchema(only=("iddef_service", "name", "teaser", "description", "icon_description", "media"))))
    promotions = fields.List(fields.Nested(BookPromotionSchema(only=("idbook_hotel", "idop_promotions"))))
    payment = fields.Nested(PaymentReservationSchema(only=("card_number", "holder_first_name", "holder_last_name", "exp_month", "exp_year", "cvv", "card_type")))
    services = fields.List(fields.Integer())
    cancelation_policies = fields.List(fields.Dict())
    guarantee_policies = fields.List(fields.Dict())
    tax_policies = fields.List(fields.Dict())
    general_data = fields.Dict()
    property_media = fields.List(fields.Nested(publicGetListMedia), dump_only=True)
    trade_name = fields.String(dump_only=True)
    code_reservation = fields.String(dump_only=True)
    property_detail = fields.Nested(PropertyBookSchema(), dump_only=True)
    status = fields.String(dump_only=True)
    idbook_status = fields.Integer(dump_only=True, data_key="status_code")
    exchange_rate = fields.Float()
    promo_amount = fields.Float(dump_only=True)
    discount_percent = fields.Float()
    discount_amount = fields.Float()
    total_gross = fields.Float(data_key="total_crossout")
    amount_pending_payment = db.Column(db.Float, nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)
    total = fields.Float(dump_only=True)
    country_fee = fields.Float()
    total_service = fields.Float()
    promotion_amount = fields.Float(dump_only=True)
    expiry_date = fields.DateTime(format="%Y-%m-%d %H:%M", dump_only=True)
    cancelation_date = fields.DateTime("%Y-%m-%d")
    visible_reason_cancellation = fields.Integer()
    modification_date_booking = fields.DateTime("%Y-%m-%d %H:%M:%S", dump_only=True)
    payment_currency = fields.String(dump_only=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    country_code = fields.String(dump_only=True)
    brand_code = fields.String(dump_only=True)
    web_address = fields.String(dump_only=True)
    address = fields.String(dump_only=True)
    resort_phone = fields.String(dump_only=True)
    resort_email = fields.String(dump_only=True)
    reservation_email = fields.String(dump_only=True)
    channel_url = fields.String(dump_only=True)
    sender = fields.String(dump_only=True)
    amount_pending_payment = fields.Float(dump_only=True)
    amount_paid = fields.Float(dump_only=True)
    promo_code_text = fields.String(dump_only=True)
    Hotel_Name = fields.String(attribute =  "tr_name", dump_only = True)
    Property_Code = fields.String(attribute = "pr_code", dump_only = True)
    Currency_Code = fields.String(attribute = "ms_code", dump_only = True)
    Market_Description = fields.String(attribute = "ms_description")
    Country_Name = fields.String(atirbute = "co_name", dump_only = True)
    Country_Code = fields.String(attribute = "co_code", dump_only = True)
    Channel_ID = fields.Integer(attribute = "ch_id", dump_only = True)
    Channel_Name = fields.String(attribute = "ch_name", dump_only = True)
    Currency_ID = fields.Integer(attribute = "cu_idcurrency", dump_only = True)
    Currency_Code = fields.String(attribute = "cu_code", dump_only = True)
    Currency_Description = fields.String(attribute = "currency_description")
    Language_ID = fields.Integer(attribute = "lan_id", dump_only = True)
    Language_Code = fields.String(attribute = "lan_code", dump_only = True)
    Language_Description = fields.String(attribute = "language_description")
    BookStatus_Name = fields.String(attribute = "bs_name", dump_only = True)
    BookStatus_Code = fields.String(attribute = "bs_code", dump_only = True)
    BookStatus_Description = fields.String(attribute = "bs_description", dump_only = True)
    
    @validates_schema
    def validate_reservation(self, data, **kwargs):
        if not data["on_hold"] and not bool(data["payment"]):
            raise ValidationError("payment data is required")

class BookHotelReservationChangeSchema(ma.Schema):
    idbook_hotel = fields.Integer()
    idbook_customer = fields.Integer()
    #iddef_property = fields.Integer(required=True)
    iddef_brand = fields.Integer()
    property_code = fields.String(required=True, validate=validate.Length(max=6))
    from_date = fields.DateTime("%Y-%m-%d")
    to_date = fields.DateTime("%Y-%m-%d")
    nights = fields.Integer()
    total_rooms = fields.Integer()
    market_code = fields.String(required=True, validate=validate.Length(max=10))
    iddef_channel = fields.Integer(required=True)
    lang_code = fields.String(required=True, validate=validate.Length(max=10))
    currency_code = fields.String(required=True, validate=validate.Length(max=10))
    promo_code = fields.String(validate=validate.Length(max=50))
    #special_request = fields.String(validate=validate.Length(max=250))
    comments = fields.List(fields.Nested(BookHotelCommentUpdateSchema(only=("idbook_hotel_comment", "text", "visible_to_guest", "source", \
        "source_text", "estado", "usuario_creacion", "fecha_creacion"))))
    on_hold = fields.Boolean()
    customer = fields.Nested(BookCustomerReservationSchema(only=("title", "first_name", "last_name", "dialling_code", "phone_number", "email", "birthdate", "company", "address")), required=True)
    rooms = fields.List(fields.Nested(BookHotelRoomReservationChangeSchema(only=("idbook_hotel_room", "iddef_room_type", "idop_rate_plan", "pax",\
        "trade_name_room", "prices", "discount_percent", "discount_amount", "total_gross", "total", "media", "rateplan_name",\
        "rates", "rates_fix", "total_to_paid_room", "total_room"))))
    services_info = fields.List(fields.Nested(BookExtraServiceReservationSchema(only=("iddef_service", "name", "teaser", "description", "icon_description", "media"))))
    promotions = fields.List(fields.Nested(BookPromotionSchema(only=("idbook_hotel", "idop_promotions"))))
    payment = fields.Nested(PaymentReservationSchema(only=("card_number", "holder_first_name", "holder_last_name", "exp_month", "exp_year", "cvv", "card_type")))
    services = fields.List(fields.Integer())
    cancelation_policies = fields.List(fields.Dict())
    guarantee_policies = fields.List(fields.Dict())
    tax_policies = fields.List(fields.Dict())
    general_data = fields.Dict()
    property_media = fields.List(fields.Nested(publicGetListMedia), dump_only=True)
    trade_name = fields.String(dump_only=True)
    code_reservation = fields.String(dump_only=True)
    property_detail = fields.Nested(PropertyBookSchema(), dump_only=True)
    status = fields.String(dump_only=True)
    idbook_status = fields.Integer(dump_only=True, data_key="status_code")
    exchange_rate = fields.Float()
    discount_percent = fields.Float()
    discount_amount = fields.Float()
    total_gross = fields.Float(data_key="total_crossout")
    total = fields.Float()
    is_refund = fields.Boolean()
    amound_refund = fields.Float()
    country_fee = fields.Float()
    total_service = fields.Float()
    promotion_amount = fields.Float(dump_only=True)
    expiry_date = fields.DateTime(format="%Y-%m-%d %H:%M", dump_only=True)
    payment_currency = fields.String(dump_only=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    country_code = fields.String(dump_only=True)
    brand_code = fields.String(dump_only=True)
    web_address = fields.String(dump_only=True)
    address = fields.String(dump_only=True)
    resort_phone = fields.String(dump_only=True)
    resort_email = fields.String(dump_only=True)
    reservation_email = fields.String(dump_only=True)
    external_payment = fields.Boolean(required=True)
    only_save = fields.Boolean(required=True)

class BookHotelReservationChangeRSchema(ma.Schema):
    idbook_hotel = fields.Integer()
    idbook_customer = fields.Integer()
    #iddef_property = fields.Integer(required=True)
    iddef_brand = fields.Integer()
    property_code = fields.String(required=True, validate=validate.Length(max=6))
    from_date = fields.DateTime("%Y-%m-%d")
    to_date = fields.DateTime("%Y-%m-%d")
    nights = fields.Integer()
    total_rooms = fields.Integer()
    market_code = fields.String(required=True, validate=validate.Length(max=10))
    iddef_channel = fields.Integer(required=True)
    lang_code = fields.String(required=True, validate=validate.Length(max=10))
    currency_code = fields.String(required=True, validate=validate.Length(max=10))
    promo_code = fields.String(validate=validate.Length(max=50))
    #special_request = fields.String(validate=validate.Length(max=250))
    on_hold = fields.Boolean()
    customer = fields.Nested(BookCustomerReservationSchema(only=("title", "first_name", "last_name", "dialling_code", "phone_number", "email", "birthdate", "company", "address")), required=True)
    rooms = fields.List(fields.Nested(BookHotelRoomReservationChangeSchema(only=("idbook_hotel_room", "iddef_room_type", "idop_rate_plan", "pax",\
        "trade_name_room", "prices", "discount_percent", "discount_amount", "total_gross", "total", "media", "rateplan_name"))))
    promotions = fields.List(fields.Nested(BookPromotionSchema(only=("idbook_hotel", "idop_promotions"))))
    payment = fields.Nested(PaymentReservationSchema(only=("card_number", "holder_first_name", "holder_last_name", "exp_month", "exp_year", "cvv", "card_type")))
    services = fields.List(fields.Nested(BookExtraServiceReservationSchema(only=("iddef_service", "name", "teaser", "description", "icon_description", "media"))))
    cancelation_policies = fields.List(fields.Dict())
    guarantee_policies = fields.List(fields.Dict())
    tax_policies = fields.List(fields.Dict())
    general_data = fields.Dict()
    property_media = fields.List(fields.Nested(publicGetListMedia), dump_only=True)
    trade_name = fields.String(dump_only=True)
    code_reservation = fields.String(dump_only=True)
    property_detail = fields.Nested(PropertyBookSchema(), dump_only=True)
    status = fields.String(dump_only=True)
    idbook_status = fields.Integer(dump_only=True, data_key="status_code")
    exchange_rate = fields.Float()
    discount_percent = fields.Float()
    discount_amount = fields.Float()
    total_gross = fields.Float(data_key="total_crossout")
    total = fields.Float(dump_only=True)
    country_fee = fields.Float()
    total_service = fields.Float()
    promotion_amount = fields.Float(dump_only=True)
    expiry_date = fields.DateTime(format="%Y-%m-%d %H:%M", dump_only=True)
    payment_currency = fields.String(dump_only=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    country_code = fields.String(dump_only=True)
    brand_code = fields.String(dump_only=True)
    web_address = fields.String(dump_only=True)
    address = fields.String(dump_only=True)
    resort_phone = fields.String(dump_only=True)
    resort_email = fields.String(dump_only=True)
    reservation_email = fields.String(dump_only=True)    

class BookHotelReservationResponseSchema(BookHotelReservationSchema):    
    rooms = fields.List(fields.Nested(BookHotelRoomReservationResponseSchema(only=("idbook_hotel_room", "iddef_room_type", "idop_rate_plan", "pax",\
        "trade_name_room", "prices", "discount_percent", "discount_amount", "total_gross", "total", "media", "rateplan_name", "amount_pending_payment",\
        "amount_paid", "promo_amount"))))
    reason_cancellation = fields.String(validate=validate.Length(max=200))

class BookHotelAdminSchema(ma.Schema):

    class Meta:
        ordered = True

    idbook_hotel = fields.Integer()
    idbook_customer = fields.Integer()
    iddef_property = fields.Integer(required=True)
    code_reservation = fields.String(validate=validate.Length(max=60))
    currency_code = fields.String()
    from_date = fields.DateTime("%Y-%m-%d")
    to_date = fields.DateTime("%Y-%m-%d")
    range_dates = fields.Method("get_range_dates") #Rango de fechas: to_date-from_date
    nights = fields.Integer()
    total_rooms = fields.Integer()
    status = fields.String()
    idbook_status = fields.Integer(dump_only=True, data_key="status_code")
    expiry_date = fields.DateTime("%Y-%m-%d")
    cancelation_date = fields.DateTime("%Y-%m-%d")
    visible_reason_cancellation = fields.Integer()
    email = fields.String()
    guest_name = fields.String()
    guest_country = fields.String()
    property_name = fields.String()
    property_code = fields.String()
    adults = fields.Integer()
    child = fields.Integer()
    nights = fields.Integer()
    market_code = fields.String(required=True, validate=validate.Length(max=10))
    iddef_channel = fields.Integer(required=True)
    lang_code = fields.String(required=True, validate=validate.Length(max=10))    
    promo_code = fields.String(validate=validate.Length(max=50))    
    on_hold = fields.Boolean(required=True)
    customer = fields.Nested(BookCustomerReservationSchema(only=("title", "first_name", "last_name", "dialling_code", "phone_number", "email", "birthdate", "company", "address")))
    rooms = fields.List(fields.Nested(BookHotelRoomReservationSchema(only=("idbook_hotel_room", "iddef_room_type", "idop_rate_plan", "pax",\
        "pms_confirm_number", "trade_name_room", "prices", "discount_percent", "discount_amount", "total_gross", "total", "polices", "no_show"))))
    codes_rooms = fields.List(fields.String())
    payment = fields.Nested(PaymentReservationSchema(only=("card_number", "holder_first_name", "holder_last_name", "exp_month", "exp_year", "cvv", "card_type")))
    services_info = fields.List(fields.Nested(BookExtraServiceReservationSchema(only=("iddef_service", "name", "teaser", "description", "icon_description", "media"))))    
    comments = fields.List(fields.Nested(BookHotelCommentSchema(only=("idbook_hotel_comment", "text", "visible_to_guest", "source", \
        "source_text", "estado", "usuario_creacion", "fecha_creacion"))))    
    promotions = fields.List(fields.Nested(BookPromotionSchema(only=("idbook_hotel", "idop_promotions"))))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

    def get_range_dates(self,obj):
        self.range_dates = str(obj["to_date"]) + " - " + str(obj["from_date"])
        return self.range_dates

    @pre_dump
    def change_datetime_utc_to_cancun(self, data, many):
        for key in data.keys():
            if key in ["cancelation_date","fecha_creacion","fecha_ultima_modificacion"] and isinstance(data[key], datetime):
                data[key] = self.utc_to_cancun_datetime(data[key])
        return data

    def utc_to_cancun_datetime(self, utc_datetime, convert_default=False):
        default_datetime = datetime.strptime('1900-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')

        if utc_datetime == default_datetime and not convert_default:
            new_datetime = utc_datetime
        else:
            new_datetime = utc_datetime - timedelta(hours=5)
        
        return new_datetime

class EmailReservationSchema(ma.Schema):
    code_reservation = fields.String()
    email = fields.String()
    name = fields.String()

class CancelReservationSchema(ma.Schema):
    idbook_hotel = fields.Integer()
    iddef_property = fields.Integer()
    idbook_status = fields.Integer()
    reason_cancellation = fields.String(validate=validate.Length(max=250))
    visible_reason_cancellation = fields.Integer()

class BookHotelLogSchema(ma.Schema):

    class Meta:
        ordered = True

    idbook_hotel = fields.Integer()
    idbook_customer = fields.Integer()
    iddef_property = fields.Integer(required=True)
    code_reservation = fields.String(validate=validate.Length(max=60))
    currency_code = fields.String()
    from_date = fields.DateTime("%Y-%m-%d")
    to_date = fields.DateTime("%Y-%m-%d")
    range_dates = fields.Method("get_range_dates") #Rango de fechas: to_date-from_date
    nights = fields.Integer()
    total_rooms = fields.Integer()
    total = fields.Float()
    status = fields.String()
    idbook_status = fields.Integer(dump_only=True, data_key="status_code")
    expiry_date = fields.DateTime("%Y-%m-%d")
    cancelation_date = fields.DateTime("%Y-%m-%d")
    visible_reason_cancellation = fields.Integer()
    email = fields.String()
    guest_name = fields.String()
    guest_country = fields.String()
    property_name = fields.String()
    property_code = fields.String()
    adults = fields.Integer()
    child = fields.Integer()
    nights = fields.Integer()
    market_code = fields.String(required=True, validate=validate.Length(max=10))
    iddef_channel = fields.Integer(required=True)
    lang_code = fields.String(required=True, validate=validate.Length(max=10))    
    promo_code = fields.String(validate=validate.Length(max=50))    
    on_hold = fields.Boolean(required=True)
    customer = fields.Nested(BookCustomerReservationSchema(only=("title", "first_name", "last_name", "dialling_code", "phone_number", "email", "birthdate", "company", "address")))
    rooms = fields.List(fields.Nested(BookHotelRoomReservationSchema(only=("idbook_hotel_room", "iddef_room_type", "idop_rate_plan", "pax",\
        "pms_confirm_number", "trade_name_room", "prices", "discount_percent", "discount_amount", "total_gross", "total", "polices"))))
    codes_rooms = fields.List(fields.String())
    payment = fields.Nested(PaymentReservationSchema(only=("card_number", "holder_first_name", "holder_last_name", "exp_month", "exp_year", "cvv", "card_type")))
    services_info = fields.List(fields.Nested(BookExtraServiceReservationSchema(only=("iddef_service", "name", "teaser", "description", "icon_description", "media"))))
    comments = fields.List(fields.Nested(BookHotelCommentSchema(only=("idbook_hotel_comment", "text", "visible_to_guest", "source", \
        "source_text", "estado", "usuario_creacion", "fecha_creacion"))))
    promotions = fields.List(fields.Nested(BookPromotionSchema(only=("idbook_hotel", "idop_promotions"))))
    estado = fields.Integer()
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    modification_date_booking = fields.DateTime("%Y-%m-%d %H:%M:%S")

    def get_range_dates(self,obj):
        self.range_dates = str(obj["to_date"]) + " - " + str(obj["from_date"])
        return self.range_dates

class BookHotelFilterSchema(ma.Schema):
    iddef_property = fields.Integer()
    property_code = fields.String()
    property_name = fields.String()
    idbook_hotel = fields.Integer()
    code_reservation = fields.String(validate=validate.Length(max=60))
    currency_code = fields.String()
    from_date = fields.DateTime("%Y-%m-%d")
    to_date = fields.DateTime("%Y-%m-%d")
    status = fields.String()
    idbook_status = fields.Integer()
    total = fields.Integer()
    codes_rooms = fields.List(fields.String())
    pms_confirm_numbers = fields.String()
    guest_name = fields.String()
    email = fields.String()
    guest_country = fields.String()
    adults = fields.Integer()
    child = fields.Integer()
    nights = fields.Integer()
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class BookHotelReservationDuplicateSchema(ma.Schema):
    property_code = fields.String(required=True, validate=validate.Length(max=6))
    from_date = fields.DateTime("%Y-%m-%d")
    to_date = fields.DateTime("%Y-%m-%d")
    market_code = fields.String(required=True, validate=validate.Length(max=10))
    iddef_channel = fields.Integer(required=True)
    lang_code = fields.String(required=True, validate=validate.Length(max=10))
    currency_code = fields.String(required=True, validate=validate.Length(max=10))
    promo_code = fields.String(validate=validate.Length(max=50))
    special_request = fields.String(validate=validate.Length(max=250))
    on_hold = fields.Boolean(required=True)
    customer = fields.Nested(BookCustomerReservationSchema(only=("title", "first_name", "last_name", "dialling_code", "phone_number", "email", "birthdate", "company", "address")), required=True)
    rooms = fields.List(fields.Nested(BookHotelRoomReservationSchema(only=("idbook_hotel_room", "iddef_room_type", "idop_rate_plan", "pax",\
    "trade_name_room", "prices", "discount_percent", "discount_amount", "total_gross", "total", "media", "rateplan_name", "promo_amount"))))
    services = fields.List(fields.Integer())