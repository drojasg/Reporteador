from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate
from common.base_audit import BaseAudit

class ReportSetting(db.Model, BaseAudit):
    __tablename__ = "report_setting"
    
    idreport_setting = db.Column(db.Integer, primary_key=True)
    subject_letter = db.Column(db.String, nullable=False)
    reports = db.Column(db.JSON(), nullable=False, default=[])
    date_window = db.Column(db.Integer, nullable=False)
    date_window_custom = db.Column(db.JSON(), nullable=False, default={})
    subscription = db.Column(db.Integer, nullable=False)
    type_recurrence = db.Column(db.Integer, nullable=False)
    recurrence = db.Column(db.JSON(), nullable=False, default=[])
    time = db.Column(db.Time, default="00:00:00")
    emails = db.Column(db.JSON(), nullable=False, default=[])
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class ReportSettingSchema(ma.Schema):
    idreport_setting = fields.Integer()
    subject_letter = fields.String(required=True, validate=validate.Length(max=150))
    reports = fields.List(fields.Integer(),required=True)
    date_window = fields.Integer(required=True)
    date_window_custom = fields.Dict(required=True)
    subscription = fields.Integer(required=True)
    type_recurrence = fields.Integer(required=True)
    recurrence = fields.List(fields.Integer(),required=True)
    time = fields.Time(required=True)
    emails = fields.List(fields.String(),required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")