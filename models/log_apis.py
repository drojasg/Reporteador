from datetime import datetime

from config import db, ma
from marshmallow import Schema, fields, validate

class LogApis(db.Model):
    __tablename__ = "log_apis"

    idlog_apis = db.Column(db.Integer, primary_key=True)
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

class LogApisSchema(ma.Schema):
    idlog_apis = fields.Integer()
    url = fields.String(validate=validate.Length(max = 250))
    request_method = fields.String(validate=validate.Length(max = 250))
    request_headers = fields.Dict()
    request_data = fields.Dict()
    response_headers = fields.Dict()
    response_data = fields.Dict()
    username = fields.String(validate=validate.Length(max = 45))
    estado = fields.Integer()
    date_start = fields.DateTime("%Y-%m-%d %H:%M:%S")
    date_end = fields.DateTime("%Y-%m-%d %H:%M:%S")
    limit = fields.Integer()


class LogApisSchemaList(ma.Schema):
    idlog_apis = fields.Integer()
    url = fields.String(validate=validate.Length(max = 250))
    request_method = fields.String(validate=validate.Length(max = 250))
    request_headers = fields.Dict()
    request_data = fields.Dict()
    request_timestamp = fields.DateTime("%Y-%m-%d %H:%M:%S")
    response_headers = fields.Dict()
    response_data = fields.Dict()
    response_timestamp = fields.DateTime("%Y-%m-%d %H:%M:%S")
    username = fields.String(validate=validate.Length(max = 45))
    estado = fields.Integer()
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

