from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate

class PolicyCancellationOption(db.Model):
    __tablename__ = "def_policy_cancellation_option"

    iddef_policy_cancellation_option = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(50), nullable=False)
    hours = db.Column(db.Integer)
    estado = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class PolicyCancellationOptionSchema(ma.Schema):    
    iddef_policy_cancellation_option = fields.Integer()
    text = fields.String(required=True,validate=validate.Length(max=50))
    hours = fields.Integer()
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")