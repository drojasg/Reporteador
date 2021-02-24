from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate
from models.channel import Channel, ChannelSchema, ChannelRefSchema
from models.auth_assignment import AuthAssignment
from common.util import Util

class Credentials(db.Model):
    __tablename__= "def_credentials"
    #__table_args__ ={'extended_existing': True}

    iddef_credentials = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(45), nullable=False)
    description = db.Column(db.String(150), nullable=False)
    api_key = db.Column(db.String(150), nullable=False)
    iddef_channel = db.Column(db.Integer, db.ForeignKey("def_channel.iddef_channel"), nullable=False)
    restricted_ip = db.Column(db.Integer(), nullable=False)
    ip_list_allowed= db.Column(db.JSON(), nullable=False)
    restricted_dns = db.Column(db.Integer(), nullable=False)
    dns_list_allowed = db.Column(db.JSON(), nullable= False)
    estado = db.Column(db.Integer, nullable=False, default=1)
    usuario_creacion = db.Column(db.String, nullable=False, default = "")
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.now)
    usuario_ultima_modificacion = db.Column(db.String, nullable=False, default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, nullable=False, default="1900-01-01 00:00:00", onupdate = datetime.now)
    roles = db.relationship('AuthAssignment', backref="credential", lazy="joined",
        primaryjoin="and_(Credentials.iddef_credentials == AuthAssignment.credentials_id, AuthAssignment.estado == 1)")

class CredentialsSchema(ma.Schema):
    iddef_credentials= fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(max=45))
    description = fields.String(required=True, validate=validate.Length(max=150))
    api_key = fields.String(required=False,validate=validate.Length(max=150))
    iddef_channel = fields.Integer()
    restricted_ip = fields.Integer(required=True, validate=validate.Length(max=4))
    ip_list_allowed = fields.Dict()
    restricted_dns = fields.Integer(required=True, validate=validate.Length(max=4))
    dns_list_allowed = fields.Dict()
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")    

class AddCredentialsSchema(ma.Schema):
    iddef_credentials= fields.Integer(dump_only=True)
    name = fields.String(required=True)
    description = fields.String(required=True)
    api_key = fields.String(required=False)
    iddef_channel = fields.Integer()
    restricted_ip = fields.Integer(required=True)
    ip_list_allowed =  fields.List(fields.String())
    restricted_dns = fields.Integer(required=True)
    dns_list_allowed =  fields.List(fields.String())
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, default="")
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45), default = True)
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")    

class AddCredentialsChanelNameSchema(ma.Schema):
    iddef_credentials= fields.Integer(dump_only=True)
    channel_name = fields.String()
    #fields.List(fields.Nested(ChannelSchema))
    name = fields.String(required=True)
    description = fields.String(required=True)
    api_key = fields.String(required=False)
    iddef_channel = fields.Integer()
    restricted_ip = fields.Integer(required=True)
    ip_list_allowed =  fields.List(fields.String())
    restricted_dns = fields.Integer(required=True)
    dns_list_allowed =  fields.List(fields.String())
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, default="")
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45), default = True)
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")  