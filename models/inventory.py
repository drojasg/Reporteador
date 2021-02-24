from datetime import datetime
from config import db, ma
from marshmallow import Schema, fields, validate

class Inventory(db.Model):
    __tablename__ = "op_inventory"

    idop_inventory = db.Column(db.Integer, primary_key=True)
    idRoom_type_category = db.Column(db.Integer)
    avail_rooms = db.Column(db.Integer)
    efective_date = db.Column(db.Date, nullable=False)
    estado = db.Column(db.Integer)
    idProperty = db.Column(db.Integer)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class InventorySchema(ma.Schema):    
    idop_inventory = fields.Integer()
    idRoom_type_category = fields.Integer(required=True)
    avail_rooms = fields.Integer()
    efective_date = fields.Date(required=True)
    idProperty = fields.Integer(required=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(required=True, validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class GetDataRoomsInventorySchema(ma.Schema):
    date = fields.Date(required=True)
    rooms = fields.List(fields.Nested("GetRoomsSchema"),required=True, many=True)

class GetRoomsSchema(ma.Schema):
    room_code = fields.String(required=True,validate=validate.Length(max=10))
    count = fields.Integer()

class SaveInventorySchema(ma.Schema):    
    hotel_code = fields.String(required=True)
    rooms = fields.List(fields.Nested("GetDataRoomsInventorySchema"),required=True, many=True)