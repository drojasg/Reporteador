from datetime import datetime, date
from time import time
from config import db, ma
from marshmallow import Schema, fields, validate
from models.property import Property
from models.sistemas import Sistemas
from models.restriction import Restriction, RestrictionSchema

class CrossOutConfig(db.Model):
    __tablename__="op_cross_out_config"
    __table_args__ = {'extend_existing': True}
    dates_apply = None

    idop_cross_out_config = db.Column(db.Integer,primary_key=True)
    cross_out_name = db.Column(db.String(45),nullable=False)
    #iddef_property = db.Column(db.Integer,db.ForeignKey("def_property.iddef_property"), nullable=False)
    #cross_out_config_property = db.relationship('Property', backref=db.backref('op_cross_out_config', lazy='dynamic'))
    id_sistema = db.Column(db.Integer,db.ForeignKey("op_sistemas.idop_sistemas"), nullable=False)
    cross_out_config_sistemas = db.relationship('Sistemas', backref=db.backref('op_cross_out_config', lazy='dynamic'))
    date_start = db.Column(db.Date, nullable=False)
    date_end = db.Column(db.Date, nullable=False)
    #time_start = db.Column(db.Time, nullable=False)
    #time_end = db.Column(db.Time, nullable=False)
    percent = db.Column(db.Integer,nullable=False)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class CrossOutConfigSchema(ma.Schema):
    idop_cross_out_config = fields.Integer(dump_only=True)
    #iddef_property = fields.Integer(required=True)
    cross_out_name = fields.String(required=True)
    id_sistema = fields.Integer(required=True)
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    #time_start = fields.Time(required=True)
    #time_end = fields.Time(required=True)
    percent = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True,validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class CrossOutConfigResSchema(ma.Schema):
    idop_cross_out_config = fields.Integer(dump_only=True)
    #iddef_property = fields.Integer(required=True)
    cross_out_name = fields.String(required=True)
    id_sistema = fields.Integer(required=True)
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    restriction = fields.List(fields.Integer(),required=True)
    #time_start = fields.Time(required=True)
    #time_end = fields.Time(required=True)
    percent = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True,validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetCrossOutConfigSchema(ma.Schema):
    idop_cross_out_config = fields.Integer(dump_only=True)
    #iddef_property = fields.Integer()
    cross_out_name = fields.String()
    id_sistema = fields.Integer()
    date_start = fields.Date()
    date_end = fields.Date()
    #time_start = fields.Time()
    #time_end = fields.Time()
    percent = fields.Integer()
    restriction = fields.List(fields.Nested(RestrictionSchema))
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetListCrossOutConfigSchema(ma.Schema):
    idop_cross_out_config = fields.Integer(dump_only=True)
    idop_rateplan = fields.Integer(required=True, load_only=True)
    iddef_property = fields.Integer(required=True, load_only=True)
    id_sistema = fields.Integer(required=True, load_only=True)
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    time_start = fields.Time()
    time_end = fields.Time()
    percent = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class ResponseExternalCrossout(ma.Schema):

    channel_id = fields.Integer(dump_only=True)
    crossout = fields.Float(dump_only=True)

class GetExternalCrossout(ma.Schema):

    system = fields.Integer(load_only=True)
    channels = fields.List(fields.Integer(),load_only=True)
    date_start = fields.Date(load_only=True)
    date_end = fields.Date(load_only=True)

    item = fields.List(fields.Nested(ResponseExternalCrossout),dump_only=True)

class GetListSearchCrossOutConfigSchema(ma.Schema):
    idop_cross_out_config = fields.Integer(dump_only=True)
    cross_out_config_property = ma.Pluck("PropertySchema", 'property_code')
    cross_out_config_sistemas = ma.Pluck("SistemasSchema", 'nombre')
    date_start = fields.Date()
    date_end = fields.Date()
    time_start = fields.Time()
    time_end = fields.Time()
    percent = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")