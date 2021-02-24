from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from common.util import Util

class Policies_Schema(ma.Schema):
    cancel_policy = fields.String()
    guarantee_policy = fields.String()
    tax_policy = fields.String()

class Dialy_Promotions_Schema(ma.Schema):
    value_discount = fields.Float()
    id_promotion = fields.Integer()
    code = fields.String()

class Dialy_Rates_Schema(ma.Schema):
    promotions = fields.Nested(Dialy_Promotions_Schema,allow_none=True)
    tax_amount = fields.Float()
    amount = fields.Float()
    pms_amount = fields.Float(dump_only=True,attribute="amount_pms")
    amount_to_pms = fields.Float(load_only=True,data_key="pms_amount")
    percent_discount = fields.Integer()
    amount_crossout = fields.Float()
    efective_date = fields.Date()
    promotion_amount = fields.Float(default=0.0)

class Rates_Plan_Schema(ma.Schema):
    room = fields.Integer(data_key="iddef_room_type", load_only=True)
    iddef_room_type = fields.Integer(attribute="room",dump_only=True)
    property = fields.Integer()
    adults = fields.Integer()
    minors = fields.Integer()
    date_end_promotion = fields.DateTime()
    timer_on = fields.Boolean()
    apply_room_free = fields.Boolean(data_key="promo_free_apply",load_only=True)
    promo_free_apply = fields.Boolean(attribute="apply_room_free",dump_only=True,default=False)
    rateplan = fields.Integer(data_key="idop_rate_plan", load_only=True)
    idop_rate_plan = fields.Integer(attribute="rateplan", dump_only=True)
    nights = fields.Integer()
    exange_amount = fields.Float()
    total = fields.Float()
    total_crossout = fields.Float(data_key="total_discount",load_only=True)
    total_discount = fields.Float(attribute="total_crossout",dump_only=True)
    total_percent_discount = fields.Integer()
    avg_total = fields.Float()
    avg_total_discount = fields.Integer()
    price_per_day = fields.List(fields.Nested(Dialy_Rates_Schema))
    rate_plan_name = fields.String()
    policies = fields.Nested(Policies_Schema)

class Promotion_Schema(ma.Schema):
    lang_code = fields.String(load_only=True, required=True)
    market = fields.String(load_only=True, required=True)
    date_start = fields.Date(load_only=True, required=True)
    date_end = fields.Date(load_only=True, required=True)
    currency = fields.String(load_only=True, required=True)
    promocode = fields.String(load_only=True)
    promo_applied = fields.Boolean(load_only=True)
    paxes = fields.Dict(fields.String(),fields.Integer(),load_only=True, required=True, data_key="rooms")
    rates = fields.List(fields.Nested(Rates_Plan_Schema),load_only=True,required=True)