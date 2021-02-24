from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from models.property import Property
from models.room_type_category import RoomTypeCategory
from models.rateplan import RatePlan
from models.category_type_pax import CategoryTypePax
from common.util import Util

class RatesPromotions(db.Model):
    __tablename__ = "oprates_promotions"
    
    idoprates_promotions = db.Column(db.Integer, primary_key=True)
    promotion_code = db.Column(db.String(45),nullable=False)
    idproperty = db.Column(db.Integer,db.ForeignKey("def_property.iddef_property"), nullable=False)
    idrate_plan = db.Column(db.Integer,db.ForeignKey("op_rateplan.idop_rateplan"), nullable=False)
    idroom_type_category = db.Column(db.Integer,db.ForeignKey("def_room_type_category.iddef_room_type_category"), nullable=False)
    idpax_type = db.Column(db.Integer,db.ForeignKey("def_category_type_pax.iddef_category_type_pax"), nullable=False)
    factor_type = db.Column(db.String(45),nullable=False)
    value = db.Column(db.Float, nullable=False)
    booking_win_start = db.Column(db.Date)
    booking_win_end = db.Column(db.Date)
    travel_win_start = db.Column(db.Date)
    travel_win_end = db.Column(db.Date)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)
    
class RatesPromotionsSchema(ma.Schema):
    
    idoprates_promotions = fields.Integer()
    promotion_code = fields.String(validate=validate.Length(max=45),required=True)
    idproperty = fields.Integer(required=True)
    idrate_plan = fields.Integer(required=True)
    idroom_type_category = fields.Integer(required=True)
    idpax_type = fields.Integer(required=True)
    factor_type = fields.String(validate=validate.Length(max=45),required=True)
    value = fields.Decimal(required=True)
    booking_win_start = fields.Date(required=True)
    booking_win_end = fields.Date(required=True)
    travel_win_start = fields.Date(required=True)
    travel_win_end = fields.Date(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")