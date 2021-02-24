from datetime import datetime
from config import db, ma
from models.languaje import Languaje
from models.property import Property
from marshmallow import Schema, fields, validate
from common.base_audit import BaseAudit

class calendarData(ma.Schema, BaseAudit):
    property_code = fields.String(load_only=True,required=True)
    date_start = fields.Date(load_only=True,required=True)
    date_end = fields.Date(load_only=True,required=True)
    market = fields.String(load_only=True,required=True)
    currency = fields.String(load_only=True,required=True)
    date_specified = fields.Boolean(load_only=True)

    efective_date = fields.Date(dump_only=True)
    dialy_rate = fields.Decimal(dump_only=True, as_string=True, places=2)
    is_offer = fields.Bool(dump_only=True)
    is_close = fields.Bool(dump_only=True)

class calendarItemRate(ma.Schema):
    date_start = fields.Date(dump_only=True)
    date_end = fields.Date(dump_only=True)
    amount = fields.Integer(dump_only=True)

class calendarItemOfer(ma.Schema):
    date_start = fields.Date(dump_only=True)
    date_end = fields.Date(dump_only=True)
    ofer = fields.Bool(dump_only=True)

class calendarItemClose(ma.Schema):
    date_start = fields.Date(dump_only=True)
    date_end = fields.Date(dump_only=True)
    close = fields.Bool(dump_only=True)

class calendarData2(ma.Schema):
    property_code = fields.String(load_only=True,required=True)
    date_start = fields.Date(load_only=True,required=True)
    date_end = fields.Date(load_only=True,required=True)
    market = fields.String(load_only=True,required=True)
    currency = fields.String(load_only=True,required=True)

    rates = fields.List(fields.Nested(calendarItemRate))
    oferts = fields.List(fields.Nested(calendarItemOfer))
    close_date = fields.List(fields.Nested(calendarItemClose))

class calendarItemPrices(ma.Schema):
    date_start = fields.Date()
    date_end = fields.Date()
    id_pax = fields.Integer()
    amount = fields.Float()

class calendarSave(ma.Schema):
    id_property = fields.Integer(load_only=True,required=True)
    id_room = fields.Integer(load_only=True,required=True)
    id_rate_plan = fields.Integer(load_only=True,required=True)
    prices = fields.List(fields.Nested(calendarItemPrices), required=True)

class calendarAvailRoom(ma.Schema):
    id_property = fields.Integer(required=True)
    id_room_type = fields.Integer(required=True)
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)

class calendarDates(ma.Schema):
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    close = fields.Bool(required=True)

class calendarRatePlan(ma.Schema):
    rateplan_id = fields.Integer(required=True)
    dates = fields.List(fields.Nested(calendarDates), required=True)

class calendarDisabledRoom(ma.Schema):
    id_property = fields.Integer(required=True)
    id_room_type = fields.Integer(required=True)
    rateplans = fields.List(fields.Nested(calendarRatePlan), required=True)

class calendarMinMaxSchema(ma.Schema):
    id_property = fields.Integer(required=True, load_only=True)
    id_room = fields.Integer(required=True, load_only=True)
    id_rate_plan = fields.Integer(required=True, load_only=True)
    date_start = fields.Date(required=True, load_only=True)
    date_end = fields.Date(required=True, load_only=True)

class calendarMinMaxDates(ma.Schema):
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    value = fields.Integer(required=True)

class calendarRestrictionBy(ma.Schema):
    id_restriction_type = fields.Integer(required=True, load_only=True)
    dates = fields.List(fields.Nested(calendarMinMaxDates), required=True)

class calendarSaveMinMaxSchema(ma.Schema):
    id_property = fields.Integer(required=True, load_only=True)
    id_room = fields.Integer(required=True, load_only=True)
    id_rate_plan = fields.Integer(required=True, load_only=True)
    data = fields.List(fields.Nested(calendarRestrictionBy), required=True)