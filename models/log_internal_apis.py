from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate

class LogInternalApis(db.Model):
    __tablename__ = "log_internal_apis"

    idlog_internal_apis = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(250), nullable=False)
    request_method = db.Column(db.String(45), nullable=False)
    request_headers = db.Column(db.JSON, nullable=False, default ="{}")
    request_data = db.Column(db.JSON, nullable=False, default ="{}")
    request_timestamp = db.Column(db.DateTime)
    response_headers = db.Column(db.JSON, nullable=False, default ="{}")
    response_data = db.Column(db.JSON, nullable=False, default ="{}")
    response_timestamp = db.Column(db.DateTime)
    username = db.Column(db.String(45), nullable=False)
    estado = db.Column(db.Integer,nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
