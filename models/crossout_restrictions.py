from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate
from models.cross_out_config import CrossOutConfig, CrossOutConfigSchema
from models.restriction import Restriction, RestrictionSchema
from common.util import Util

class CrossoutRastriction(db.Model):
    __tablename__="op_crossout_restriction"
    __table_args__ = {'extend_existing': True} 

    idop_crossout_restriction = db.Column(db.Integer,primary_key=True)
    idop_crossout = db.Column(db.Integer,db.ForeignKey("op_cross_out_config.idop_cross_out_config"), nullable=False)
    iddef_restriction = db.Column(db.Integer,db.ForeignKey("def_restriction.iddef_restriction"), nullable=False)
    estado = db.Column(db.Integer,nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False, default="")
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class CrossoutRestrictionSchema(ma.Schema):
    idop_crossout_restriction = fields.Integer()
    idop_crossout = fields.Integer(required=True)
    iddef_restriction = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True,validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    crossouts = fields.Nested("CrossOutConfigSchema", many=False, exclude=Util.get_default_excludes())