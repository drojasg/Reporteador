from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate
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
    pax_number = fields.Integer(required=True,error_messages={'required':'pax_number is required'})

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