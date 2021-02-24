from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from common.util import Util
from common.base_audit import BaseAudit

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
    tax_amount = fields.Integer(attribute="country_fee")
    pms_amount = fields.Integer(attribute="amount_to_pms")

class PublicRatesSchema(ma.Schema):
    property = fields.Integer()
    room = fields.Integer()
    rateplan = fields.Integer()
    date_start = fields.Date()
    date_end = fields.Date()
    pax = fields.Dict(fields.String(),fields.Integer())
    rates = fields.List(fields.Nested(PricePerDaySchema))

class QuoteSchema(ma.Schema):
    pass