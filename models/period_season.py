from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate
from models.season import Season
from common.base_audit import BaseAudit

class PeriodSeason(db.Model, BaseAudit):
    __tablename__="def_period_season"

    iddef_period_season = db.Column(db.Integer, primary_key=True)
    iddef_season = db.Column(db.Integer, db.ForeignKey("def_season.iddef_season"), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.now)
    end_date = db.Column(db.DateTime, default=datetime.now)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(
        db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class PeriodSeasonSchema(ma.Schema):
    iddef_period_season = fields.Integer(dump_only=True)
    iddef_season = fields.Integer(required=True)
    start_date = fields.DateTime("%Y-%m-%d %H:%M:%S")
    end_date = fields.DateTime("%Y-%m-%d %H:%M:%S")
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class PeriodSeasonRefSchema(ma.Schema):
    iddef_period_season = fields.Integer(dump_only=True)
    iddef_season = fields.Integer(required=True)
    start_date = fields.DateTime("%Y-%m-%d %H:%M:%S")
    end_date = fields.DateTime("%Y-%m-%d %H:%M:%S")
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
