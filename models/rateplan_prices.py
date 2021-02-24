from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate
from models.property import Property
from models.rateplan import RatePlan
from models.room_type_category import RoomTypeCategory
from models.category_type_pax import CategoryTypePax

class RatePlanPrices(db.Model):
    __tablename__="op_rateplan_prices"
    __table_args__ = {'extend_existing': True} 

    idop_rateplan_prices = db.Column(db.Integer,primary_key=True)
    idproperty = db.Column(db.Integer,db.ForeignKey("def_property.iddef_property"), nullable=False)
    idrateplan = db.Column(db.Integer,db.ForeignKey("op_rateplan.idop_rateplan"), nullable=False)
    idroom_type = db.Column(db.Integer,db.ForeignKey("def_room_type_category.iddef_room_type_category"), nullable=False)
    idpax_type = db.Column(db.Integer,db.ForeignKey("def_category_type_pax.iddef_category_type_pax"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date_start = db.Column(db.Date)
    date_end = db.Column(db.Date)
    is_override = db.Column(db.Integer(),default=0)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class RatePlanPricesSchema(ma.Schema):
    idop_rateplan_prices = fields.Integer(dump_only=True)
    idproperty = fields.Integer(required=True)
    idrateplan = fields.Integer(required=True)
    idroom_type = fields.Integer(required=True)
    idpax_type = fields.Integer(required=True)
    amount = fields.Float()
    date_start = fields.Date()
    date_end = fields.Date()
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    is_override = fields.Integer()

class GetRatePlanPricesSchema(ma.Schema):
    idop_rateplan_prices = fields.Integer(dump_only=True)
    idproperty = fields.Integer()
    idrateplan = fields.Integer()
    idroom_type = fields.Integer()
    idpax_type = fields.Integer()
    amount = fields.Float()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    is_override = fields.Integer()