from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate

class Promotions(db.Model):
    __tablename__ = "op_promotions"
    
    idop_promotions = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    code = db.Column(db.String, nullable=False, default="")
    discounts = db.Column(db.JSON(), nullable=False, default=[])
    free_childs = db.Column(db.Integer, nullable=False)
    free_childs_conditions = db.Column(db.JSON(), nullable=False, default=[])
    free_nights = db.Column(db.Integer, nullable=False)
    free_nights_conditions = db.Column(db.JSON(), nullable=False, default=[])
    free_rooms = db.Column(db.Integer, nullable=False)
    free_rooms_conditions = db.Column(db.JSON(), nullable=False, default=[])
    length_of_stay = db.Column(db.JSON(), nullable=False, default=[])
    partial_aplication = db.Column(db.Integer, nullable=False)
    limit_sales = db.Column(db.Integer, nullable=False)
    limit_sales_count = db.Column(db.Integer, nullable=False)
    timer = db.Column(db.Integer, nullable=False)
    days_offset = db.Column(db.Integer, nullable=False)
    time_offset = db.Column(db.Time, default="00:00:00")
    percent_cross_out = db.Column(db.Integer,nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class PromotionsSchema(ma.Schema):
    idop_promotions = fields.Integer()
    name = fields.String(required=True, validate=validate.Length(max=45))
    code = fields.String(required=True, validate=validate.Length(max=45))
    discounts = fields.List(fields.Dict(),required=True)
    free_childs = fields.Integer()
    free_childs_conditions = fields.List(fields.Dict(),required=True)
    free_nights = fields.Integer()
    free_nights_conditions = fields.Dict(required=True)
    free_rooms = fields.Integer()
    free_rooms_conditions = fields.Dict(required=True)
    length_of_stay = fields.Dict(required=True)
    partial_aplication = fields.Integer()
    limit_sales = fields.Integer()
    limit_sales_count = fields.Integer()
    timer = fields.Integer()
    days_offset = fields.Integer()
    time_offset = fields.Time()
    percent_cross_out = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetAllPromotionsSchema(ma.Schema):
    idop_promotions = fields.Integer()
    name = fields.String(required=True, validate=validate.Length(max=45))
    code = fields.String(required=True, validate=validate.Length(max=45))
    discounts = fields.List(fields.Dict(),required=True,load_only=True)
    free_childs = fields.Integer(load_only=True)
    free_childs_conditions = fields.List(fields.Dict(),required=True,load_only=True)
    free_nights = fields.Integer(load_only=True)
    free_nights_conditions = fields.Dict(load_only=True,required=True)
    free_rooms = fields.Integer(load_only=True)
    free_rooms_conditions = fields.Dict(load_only=True,required=True)
    length_of_stay = fields.Dict(load_only=True,required=True)
    partial_aplication = fields.Integer(load_only=True)
    limit_sales = fields.Integer(load_only=True)
    limit_sales_count = fields.Integer(load_only=True)
    timer = fields.Integer()
    days_offset = fields.Integer()
    time_offset = fields.Time()
    percent_cross_out = fields.Integer()
    estado = fields.Integer()

class PromotionsPostSchema(ma.Schema):
    idop_promotions = fields.Integer()
    name = fields.String(required=True, validate=validate.Length(max=45))
    code = fields.String(required=True, validate=validate.Length(max=45))
    discounts = fields.List(fields.Dict(),required=True)
    free_childs = fields.Integer()
    free_childs_conditions = fields.List(fields.Dict(),required=True)
    free_nights = fields.Integer()
    free_nights_conditions = fields.Dict(required=True)
    free_rooms = fields.Integer()
    free_rooms_conditions = fields.Dict(required=True)
    length_of_stay = fields.Dict(required=True)
    partial_aplication = fields.Integer()
    limit_sales = fields.Integer()
    limit_sales_count = fields.Integer()
    timer = fields.Integer(required=True)
    days_offset = fields.Integer()
    time_offset = fields.Time()
    percent_cross_out = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    detail_restriction = fields.List(fields.Dict(),required=True)
    rate_plans = fields.List(fields.Dict(),required=True)
    #rate_plans = fields.List(fields.Nested("getRatePlansSchema"), many=True, required=True)

class PromotionsPutSchema(ma.Schema):
    idop_promotions = fields.Integer()
    name = fields.String(validate=validate.Length(max=45))
    code = fields.String(validate=validate.Length(max=45))
    discounts = fields.List(fields.Dict())
    free_childs = fields.Integer()
    free_childs_conditions = fields.List(fields.Dict(),required=True)
    free_nights = fields.Integer()
    free_nights_conditions = fields.Dict()
    free_rooms = fields.Integer()
    free_rooms_conditions = fields.Dict()
    length_of_stay = fields.Dict()
    partial_aplication = fields.Integer()
    limit_sales = fields.Integer()
    limit_sales_count = fields.Integer()
    timer = fields.Integer()
    days_offset = fields.Integer()
    time_offset = fields.Time()
    percent_cross_out = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    detail_restriction = fields.List(fields.Dict(),required=True)
    rate_plans = fields.List(fields.Dict(),required=True)