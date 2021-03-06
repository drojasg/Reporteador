from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate
from models.property import Property
from models.market_segment import MarketSegment
from models.sistemas import Sistemas
from models.rate_plan_rooms import RatePlanRooms, RatePlanRoomsSchema
from models.crossout_rate_plan import CrossoutRatePlan, CrossoutRatePlanSchema
from models.rateplan_restriction import RatePlanRestriction, RatePlanRestrictionSchema
from models.text_lang import GetTextLangSchema, PutTextLangSchema
from common.util import Util

class RatePlan(db.Model):
    __tablename__="op_rateplan"
    __table_args__ = {'extend_existing': True} 

    idop_rateplan = db.Column(db.Integer,primary_key=True)
    code = db.Column(db.String(45), nullable=False, unique=True)
    # booking_window_start = db.Column(db.DateTime, nullable=False, default='1900-01-01')
    # booking_window_end = db.Column(db.DateTime, nullable=False, default='1900-01-01')
    # travel_window_start = db.Column(db.DateTime, nullable=False, default='1900-01-01')
    # travel_window_end = db.Column(db.DateTime, nullable=False, default='1900-01-01')
    # id_market_segment = db.Column(db.Integer,db.ForeignKey("def_market_segment.iddef_market_segment"), nullable=False)
    rate_code_base = db.Column(db.String(50),default="")
    id_sistema = db.Column(db.Integer,db.ForeignKey("op_sistemas.idop_sistemas"),nullable=False)
    currency_code = db.Column(db.String(10), nullable=False, default="USD")
    rate_code_clever = db.Column(db.String(45), nullable=False, default="")
    refundable = db.Column(db.Integer, nullable=False, default=0)
    lead_time = db.Column(db.Integer, nullable=False, default=0)
    estado = db.Column(db.Integer,nullable=False, default=1)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)
    rate_plan_rooms = db.relationship('RatePlanRooms', backref=db.backref('op_rateplan', lazy='joined'))
    crossout_rate_plans = db.relationship('CrossoutRatePlan', backref=db.backref('op_rateplan', lazy='joined'))
    rateplan_restrictions = db.relationship('RatePlanRestriction', backref=db.backref('op_rateplan', lazy='joined'))

class BookingModifyRateplanGet(ma.Schema):
    lang_code = fields.String(validate=validate.Length(max=10),load_only=True, required=True)
    #currency = fields.String(required=True, validate=validate.Length(max=10),load_only=True)
    market = fields.String(required=True, validate=validate.Length(max=15),load_only=True)
    property_code = fields.String(required=True, validate=validate.Length(max=6),load_only=True)
    date_start = fields.Date(load_only=True,required=True)
    date_end = fields.Date(load_only=True,required=True)
    #promo_code = fields.String(validate=validate.Length(max=6),load_only=True)
    rooms = fields.Dict(fields.String(),fields.Integer(),load_only=True,required=True)
    room_type = fields.Integer(load_only=True,required=True)
    #rate_plan = fields.Integer(load_only=True)
    #promotions = fields.Boolean(load_only=True)
    #rooms_status = fields.Integer(load_only=True)

class RatePlanSchema(ma.Schema):
    idop_rateplan = fields.Integer()
    code = fields.String(required=True,validate=validate.Length(max=45))
    #booking_window_start = fields.Date(required=True)
    #booking_window_end = fields.Date(required=True)
    #travel_window_start = fields.Date(required=True)
    #travel_window_end = fields.Date(required=True)
    #id_market_segment = fields.Integer(required=True)
    #idProperty = fields.Integer(required=True)
    rate_code_base = fields.String()
    id_sistema = fields.Integer(required=True)
    currency_code = fields.String(required=True,validate=validate.Length(max=10))
    rate_code_clever = fields.String(required=True,validate=validate.Length(max=45))
    refundable = fields.Integer(required=True)
    lead_time = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True,validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    rate_plan_rooms = fields.Nested(RatePlanRoomsSchema, many=True, exclude=Util.get_default_excludes())
    crossout_rate_plans = fields.Nested(CrossoutRatePlanSchema, many=True, exclude=Util.get_default_excludes())
    rateplan_restrictions = fields.Nested(RatePlanRestrictionSchema, many=True, exclude=Util.get_default_excludes())

class GetRatePlanSchema(ma.Schema):
    idop_rateplan = fields.Integer(dump_only=True)
    currency_code = fields.String(validate=validate.Length(max=10))
    #booking_window_start = fields.Date()
    #booking_window_end = fields.Date()
    #travel_window_start = fields.Date()
    #travel_window_end = fields.Date()
    #id_market_segment = fields.Integer()
    #idProperty = fields.Integer()
    rate_code_base = fields.String()
    id_sistema = fields.Integer()
    rate_code_clever = fields.String(validate=validate.Length(max=45))
    refundable = fields.Integer()
    lead_time = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    rate_plan_rooms = fields.Nested(RatePlanRoomsSchema, many=True, exclude=Util.get_default_excludes())
    crossout_rate_plans = fields.Nested(CrossoutRatePlanSchema, many=True, exclude=Util.get_default_excludes())
    rateplan_restrictions = fields.Nested(RatePlanRestrictionSchema, many=True, exclude=Util.get_default_excludes())

class RatePlanIdSchema(ma.Schema):
    idop_rateplan = fields.Integer(dump_only=True)
    code = fields.String(validate=validate.Length(max=45))
    #booking_window_start = fields.Date()
    #booking_window_end = fields.Date()
    #travel_window_start = fields.Date()
    #travel_window_end = fields.Date()
    #id_market_segment = fields.Integer()
    #idProperty = fields.Integer()
    currency_code = fields.String(validate=validate.Length(max=10))
    rate_code_clever = fields.String(validate=validate.Length(max=45))
    refundable = fields.Integer()
    lead_time = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    properties = fields.List(fields.Integer)
    rooms = fields.List(fields.Integer)
    crossouts = fields.List(fields.Integer)
    restrictions = fields.List(fields.Integer)
    text_langs = fields.Nested(PutTextLangSchema, many=True, exclude=Util.get_default_excludes())
    policies = fields.List(fields.Integer)

class PostRatePlanSchema(ma.Schema):
    idop_rateplan = fields.Integer()
    code = fields.String(required=True,validate=validate.Length(max=45))
    #booking_window_start = fields.Date(required=True)
    #booking_window_end = fields.Date(required=True)
    #travel_window_start = fields.Date(required=True)
    #travel_window_end = fields.Date(required=True)
    #id_market_segment = fields.Integer(required=True)
    #idProperty = fields.Integer(required=True)
    id_sistema = fields.Integer()
    currency_code = fields.String(required=True,validate=validate.Length(max=10))
    rate_code_clever = fields.String(required=True,validate=validate.Length(max=45))
    refundable = fields.Integer(required=True)
    lead_time = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True,validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    properties = fields.List(fields.Integer)
    rooms = fields.List(fields.Integer)
    crossouts = fields.List(fields.Integer)
    restrictions = fields.List(fields.Integer)
    text_langs = fields.Nested(GetTextLangSchema, many=True)
    policies = fields.List(fields.Integer)

class RatePlanEstadoSchema(ma.Schema):
    idop_rateplan = fields.Integer(dump_only=True)
    code = fields.String(validate=validate.Length(max=45))
    #booking_window_start = fields.Date()
    #booking_window_end = fields.Date()
    #idProperty = fields.Integer()
    currency_code = fields.String(validate=validate.Length(max=10))
    rate_code_clever = fields.String(validate=validate.Length(max=45))
    refundable = fields.Integer()
    estado = fields.Integer(required=True)
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetPublicRatePlanSchema(ma.Schema):
    lang_code = fields.String(validate=validate.Length(max=10))
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    id_rate_plan = fields.Integer(required=True)
    currency = fields.String(required=True, validate=validate.Length(max=10))
    market = fields.String(validate=validate.Length(max=15))
    id_room = fields.Integer(required=True)
    id_hotel = fields.String(required=True)
    paxes = fields.Dict(fields.String(),fields.Integer())
    #paxes = fields.List(fields.Dict(fields.String(),fields.Integer()),required=True)

class GetDataRatePlan2Schema(ma.Schema):
    idop_rate_plan = fields.Integer()
    plan_code = fields.String(validate=validate.Length(max=45))
    plan_name = fields.String(validate=validate.Length(max=350))
    nights = fields.Integer()
    total = fields.Float()
    total_crossout = fields.Float()
    price_per_day = fields.List(fields.Nested("GetDataPricePerDay2Schema"), many=True)
    total_percent_discount = fields.Integer()
    night_price = fields.Float()

class GetDataPricePerDay2Schema(ma.Schema):
    nights = fields.Integer()
    amount = fields.Float()
    amount_crossout = fields.Float()
    percent_discount = fields.Integer()
    efective_date = fields.Date()