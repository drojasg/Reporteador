from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from common.util import Util
from resources.rates.RatesHelper import RatesFunctions as rateFunctions

class CalendarSchema(ma.Schema):
    property_code = fields.Integer(required=True)
    rate_plan_code = fields.Integer(required=True)
    room_type_code = fields.Integer(required=True)
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    currency_code = fields.String(required=True)
    country_code = fields.String(required=True)
    market_id = fields.Integer(required=True)

class Promotions(ma.Schema):
    promotion_code = fields.String(required=True)
    description = fields.String(required=True)
    factor_value = fields.Integer(required=True)
    idrate_factor_type = fields.String(required=True)
    amount_promotion = fields.Decimal(required=True)
    idrate_promotion = fields.String(required=True)
    travel_begin = fields.Date(required=True)
    travel_end = fields.Date(required=True)

class Prices(ma.Schema):
    pax_type = fields.String(required=True)
    group_pax = fields.String(required=True)
    amount_base = fields.Decimal(required=True)
    amount_final = fields.Decimal(required=True)
    rate_exists = fields.Boolean(required=True)
    promotions = fields.List(fields.Nested(Promotions),required=True)

class RatesDetail(ma.Schema):
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    prices = fields.List(fields.Nested(Prices),required=True)

class RatesSchema(ma.Schema):
    hotel = fields.String(required=True)
    rate_plan = fields.String(required=True)
    rate_base_code = fields.String(required=True)
    market = fields.String(required=True)
    currency_code = fields.String(required=True)
    room_type_category = fields.String(required=True)
    room_description = fields.String(required=True)
    max_ocupancy = fields.Integer(required=True)
    max_children = fields.Integer(required=True)
    include_kids = fields.Boolean(required=True)
    rates = fields.List(fields.Nested(RatesDetail),required=True)


class PublicRateSchema_v2(ma.Schema):
    class Meta:
        ordered = True

    lang_code = fields.String(validate=validate.Length(max=10),load_only=True, required=True)
    currency = fields.String(required=True, validate=validate.Length(max=10),load_only=True)
    market = fields.String(required=True, validate=validate.Length(max=15),load_only=True)
    property_code = fields.String(required=True, validate=validate.Length(max=6),load_only=True)
    date_start = fields.Date(load_only=True)
    date_end = fields.Date(load_only=True)
    promo_code = fields.String(validate=validate.Length(max=6),load_only=True)
    rooms = fields.Dict(fields.String(),fields.Integer(),load_only=True)
    room_type = fields.Integer(load_only=True)
    rate_plan = fields.Integer(load_only=True)
    promotions = fields.Boolean(load_only=True)
    room_status = fields.Integer(load_only=True)
    promo_applied = fields.Boolean(load_only=True)
    lead_time = fields.Boolean(load_only=True)
    is_free = fields.Boolean(load_only=True)
    promocode = fields.String(load_only=True)

    


class PublicRatesSchema(ma.Schema):

    class Meta:
        ordered = True

    lang_code = fields.String(validate=validate.Length(max=10),load_only=True, required=True)
    currency = fields.String(required=True, validate=validate.Length(max=10),load_only=True)
    market = fields.String(required=True, validate=validate.Length(max=15),load_only=True)
    property_code = fields.String(required=True, validate=validate.Length(max=6),load_only=True)
    date_start = fields.Date(load_only=True)
    date_end = fields.Date(load_only=True)
    promo_code = fields.String(validate=validate.Length(max=6),load_only=True)
    rooms = fields.Dict(fields.String(),fields.Integer(),load_only=True)
    room_type = fields.Integer(load_only=True)
    rate_plan = fields.Integer(load_only=True)
    promotions = fields.Boolean(load_only=True)
    room_status = fields.Integer(load_only=True)
    promo_applied = fields.Boolean(load_only=True)
    lead_time = fields.Boolean(load_only=True)
    is_free = fields.Boolean(load_only=True)
    promocode = fields.String(load_only=True)

    iddef_room_type = fields.Integer(dump_only=True,attribute="room")
    property = fields.Integer(dump_only=True)
    adults = fields.Integer(dump_only=True)
    minors = fields.Integer(dump_only=True)
    date_end_promotion = fields.DateTime(dump_only=True, format="%Y-%m-%d %H:%M:%S")
    timer_on = fields.Boolean(dump_only=True,default=False)
    promo_free_apply = fields.Boolean(dump_only=True,default=False)
    #rateplan = fields.Integer(dump_only=True)
    idop_rate_plan = fields.Integer(attribute="rateplan",dump_only=True) #id numerico del rate plan
    rate_plan_name = fields.String(validate=validate.Length(max=45),dump_only=True) #Nombre comercial del rateplan
    nights = fields.Integer(dump_only=True) #Total de noches a cobrar
    exange_amount = fields.Float(dump_only=True)
    #avg_percent_discount = fields.Integer(dump_only=True) #Promedio del porcentaje aplicado
    total = fields.Integer(dump_only=True) #Total, suma de noches
    total_discount = fields.Integer(attribute="total_crossout", dump_only=True) #Total inflado, suma de noches
    total_percent_discount = fields.Integer(dump_only=True) #Porcentaje aplicado
    avg_total = fields.Method("get_avg_price_total") #Promedio del total
    avg_total_discount = fields.Method("get_avg_price_cross") #Promedio del total inflado
    price_per_day = fields.List(fields.Nested("PricePerDaySchema"), many=True,dump_only=True) #precio por noche
    policies = fields.Dict(dump_only=True)

    def get_avg_price_total(self,obj):
        self.avg_total = int(round(float(obj["total"]/obj["nights"]),0))
        return self.avg_total

    def get_avg_price_cross(self,obj):
        self.avg_total_discount = int(round(float(obj["total_crossout"]/obj["nights"]),0))
        return self.avg_total_discount
        #return rateFunctions.calculateRate(obj["total_percent_discount"],self.avg_total)


class DialyPromotionApplySchema(ma.Schema):
    id_promotion = fields.Integer()
    code = fields.String()
    value_discount = fields.Float()

class PricePerDaySchema(ma.Schema):
    nights = fields.Integer()
    amount = fields.Integer()
    amount_crossout = fields.Integer()
    percent_discount = fields.Integer()
    efective_date = fields.Date()
    promotions = fields.Nested(DialyPromotionApplySchema,default=None)
    tax_amount = fields.Integer()
    pms_amount = fields.Integer(attribute="amount_to_pms")

class PricePerDayChangeSchema(ma.Schema):
    nights = fields.Integer()
    amount = fields.Integer()
    amount_crossout = fields.Integer()
    percent_discount = fields.Integer()
    efective_date = fields.Date()
    promotions = fields.Nested(DialyPromotionApplySchema,default=None)
    tax_amount = fields.Float()
    vaucher_discount = fields.Float()
    price_pms = fields.Float()

class PushRatesSchema(ma.Schema):
    hotel = fields.String()
    date_start = fields.Date()
    date_end= fields.Date()
    rate_plan_clever = fields.String()
    rate_plan_channel = fields.String()
    include_promotion = fields.Boolean()
    date_start_promotions = fields.Date()
    refundable = fields.Boolean()

class RoomsItem(ma.Schema):

    iddef_room_type = fields.Integer()
    idop_rate_plan = fields.Integer()
    rate_plan_name = fields.String()
    pax = fields.Dict(fields.String(),fields.Integer())
    trade_name_room = fields.String()
    key_room = fields.Integer()

class RatesWithPromotions(ma.Schema):

    class Meta:
        ordered = True

    hotel = fields.String(load_only=True,required=True)
    market = fields.String(load_only=True,required=True)
    date_start = fields.Date(load_only=True,required=True)
    date_end = fields.Date(load_only=True,required=True)
    lang_code = fields.String(load_only=True,required=True)
    currency = fields.String(load_only=True,required=True)
    promocode = fields.String(load_only=True,required=True)
    rooms = fields.List(fields.Nested(RoomsItem),load_only=True,required=True)
    is_free = fields.Boolean(load_only=True)

    promotions_applied = fields.List(fields.String(),dump_only=True,attribute="Promotion_Apply")
    promo_code_applied = fields.String(dump_only=True, attribute="Vaucher_Apply",default="")
    rates = fields.List(fields.Nested(PublicRatesSchema),dump_only=True,attribute="Prices")
    subtotal = fields.Integer(dump_only=True,default=0,attribute="Subtotal")
    total = fields.Integer(dump_only=True,default=0,attribute="Total")
    text = fields.String(dump_only=True,default="",attribute="Text")
    diference = fields.Method("calculate_dif")
    vaucher_apply = fields.Boolean(dump_only=True,default=False,attribute="vaucher_applied")
    vuaucher_error_txt = fields.String(attribute="Vuaucher_error_txt",dump_only=True)
    promotion_error_txt = fields.List(fields.String(),attribute="Promotion_error_txt",dump_only=True)
    total_tax = fields.Float(dump_only=True,default=0.0)

    def calculate_dif(self,obj):
        return int(round(obj["Subtotal"]-obj["Total"],0))

class ModifyBookingRatesDialy(ma.Schema):
    class Meta:
        ordered = True

    #nights = fields.Integer()
    amount = fields.Integer()
    #amount_crossout = fields.Integer()
    #percent_discount = fields.Integer()
    efective_date = fields.Date()
    pms_amount = fields.Integer(attribute="amount_to_pms")
    vaucher_discount = fields.Float(dump_only=True, default=0)
    #promotions = fields.Nested(DialyPromotionApplySchema,default=None)
    

class ModifyBookingPolicies(ma.Schema):

    cancel = fields.Integer(required=True)
    booking = fields.Integer(required=True)
    tax = fields.Integer(required=True)

class ModifyBookingRoomInfo(ma.Schema):

    iddef_room_type = fields.Integer()
    idop_rate_plan = fields.Integer()
    form_reference = fields.String()
    idbook_hotel_room = fields.Integer()
    pax = fields.Dict(fields.String(),fields.Integer(),load_only=True)
    policies = fields.Nested(ModifyBookingPolicies)
    rates = fields.List(fields.Nested(ModifyBookingRatesDialy))
    total_room = fields.Float(dump_only=True, attribute="total")
    total_to_pay = fields.Float(attribute="amount_to_pay",dump_only=True,default=0.0)
    total_paid = fields.Float(attribute="amount_paid",dump_only=True,default=0.0)
    room_code = fields.String(dump_only=True,default="")
    discount_total_room = fields.Float(dump_only=True,attribute="discount_room",default=0)


class ModifyBookingRates(ma.Schema):
    
    hotel = fields.String(load_only=True,required=True)
    market = fields.String(load_only=True,required=True)
    date_start = fields.Date(load_only=True,required=True)
    date_end = fields.Date(load_only=True,required=True)
    lang_code = fields.String(load_only=True,required=True)
    currency = fields.String(load_only=True,required=True)
    promocode = fields.Integer(load_only=True,required=True)
    service_amount = fields.Float(load_only=True)
    idbook_hotel = fields.Integer(load_only=True)
    rooms = fields.List(fields.Nested(ModifyBookingRoomInfo),load_only=True,required=True)

    rates = fields.List(fields.Nested(ModifyBookingRoomInfo),dump_only=True)
    total = fields.Float(dump_only=True)
    promocode_txt = fields.String(dump_only=True)
    promocode_apply = fields.Boolean(dump_only=True)
    descount = fields.Float(dump_only=True)
    subtotal = fields.Float(dump_only=True)
    total_amount_paid = fields.Float(dump_only=True,attribute="amount_paid")
    total_amount_to_pay = fields.Float(dump_only=True,attribute="amount_to_pay")
    total_amount_pending_payment = fields.Float(dump_only=True,attribute="amount_pending_payment")
    total_amount_to_pending_payment = fields.Float(dump_only=True,attribute="amount_to_pending_payment")
    total_amount_refund = fields.Float(dump_only=True,attribute="amount_refund")
    total_amount_to_refund = fields.Float(dump_only=True,attribute="amount_to_refund")

class ModifyBookingRoomInfoPayment(ma.Schema):
    idbook_hotel_room = fields.Integer()
    policies = fields.Nested(ModifyBookingPolicies,load_only=True)
    rates = fields.List(fields.Nested(ModifyBookingRatesDialy),load_only=True)
    total_room = fields.Float(dump_only=True, attribute="total")
    total_to_pay = fields.Float(attribute="amount_to_pay",dump_only=True,default=0.0)
    total_paid = fields.Float(attribute="amount_paid",dump_only=True,default=0.0)
    discount_total_room = fields.Float(dump_only=True,attribute="discount_room",default=0)

class ModifyBookingPayment(ma.Schema):
    currency = fields.String(load_only=True,required=True)
    service_amount = fields.Float(load_only=True)
    idbook_hotel = fields.Integer(load_only=True)
    rooms = fields.List(fields.Nested(ModifyBookingRoomInfoPayment),load_only=True,required=True)

    rates = fields.List(fields.Nested(ModifyBookingRoomInfoPayment),dump_only=True)
    total = fields.Float(dump_only=True)
    promocode_txt = fields.String(dump_only=True)
    promocode_apply = fields.Boolean(dump_only=True)
    descount = fields.Float(dump_only=True)
    subtotal = fields.Float(dump_only=True)
    total_amount_paid = fields.Float(dump_only=True,attribute="amount_paid")
    total_amount_to_pay = fields.Float(dump_only=True,attribute="amount_to_pay")
    total_amount_pending_payment = fields.Float(dump_only=True,attribute="amount_pending_payment")
    total_amount_to_pending_payment = fields.Float(dump_only=True,attribute="amount_to_pending_payment")
    total_amount_refund = fields.Float(dump_only=True,attribute="amount_refund")
    total_amount_to_refund = fields.Float(dump_only=True,attribute="amount_to_refund")