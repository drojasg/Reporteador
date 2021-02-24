from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from common.util import Util

class PolicyCategory(db.Model):
    __tablename__ = "def_policy_category"

    iddef_policy_category = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(300), nullable=False)
    help_text = db.Column(db.String(300), nullable=False)
    has_config = db.Column(db.Integer, nullable=False)
    options = db.Column(db.JSON, nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class PolicyCategorySchema(ma.Schema):
    iddef_policy_category = fields.Integer()
    description = fields.String(validate=validate.Length(max=300), required=True)
    help_text = fields.String(validate=validate.Length(max=300), required=True)
    has_config = fields.Integer(required=True)
    options = fields.Dict(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetPolicyCategorySchema(ma.Schema):
    iddef_policy_category = fields.Integer()
    description = fields.String(validate=validate.Length(max=300))
    help_text = fields.String(validate=validate.Length(max=300))
    has_config = fields.Integer()
    options = fields.Dict()
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")