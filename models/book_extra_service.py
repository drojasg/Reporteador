from config import db, ma
from marshmallow import Schema, fields, validate
from datetime import datetime
from common.util import Util
from models.book_extra_type import BookExtraType, BookExtraTypeSchema
from models.media import publicGetListMedia

class BookExtraService(db.Model):
    __tablename__ = "book_extra_service"

    idbook_extra_service = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(150))
    idbook_extra_type = db.Column(db.Integer, db.ForeignKey('book_extra_type.idbook_extra_type'), nullable=False)
    idbook_hotel = db.Column(db.Integer, db.ForeignKey('book_hotel.idbook_hotel'), nullable=False)
    iddef_service = db.Column(db.Integer)
    external_folio = db.Column(db.String(50))
    unit_price = db.Column(db.Float,nullable=False)
    quantity = db.Column(db.Integer,nullable=False)
    total_gross = db.Column(db.Float,nullable=False)
    discount_percent = db.Column(db.Float,nullable=False)
    discount_amount = db.Column(db.Float,nullable=False)
    fee_amount = db.Column(db.Float,nullable=False)
    total = db.Column(db.Float,nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    usuario_creacion = db.Column(db.String(45), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_ultima_modificacion = db.Column(db.String(45), default="")
    fecha_ultima_modificacion = db.Column(db.DateTime, default="1900-01-01 00:00:00", onupdate=datetime.utcnow)

class BookExtraServiceSchema(ma.Schema):

    idbook_extra_service = fields.Integer(dump_only=True)
    description = fields.String()
    idbook_extra_type = fields.Integer()
    idbook_hotel = fields.Integer()
    iddef_service = fields.Integer()
    external_folio = fields.String(validate=validate.Length(max=50))
    unit_price = fields.Float(as_string=True)
    quantity = fields.Float(as_string=True)
    total_gross = fields.Float(as_string=True)
    discount_percent = fields.Float(as_string=True)
    discount_amount = fields.Float(as_string=True)
    fee_amount = fields.Float(as_string=True)
    total = fields.Float(as_string=True)
    estado = fields.Integer()
    usuario_creacion = fields.String(validate=validate.Length(max=45))
    fecha_creacion = fields.DateTime("%Y-%m-%d %H:%M:%S")
    usuario_ultima_modificacion = fields.String(validate=validate.Length(max=45))
    fecha_ultima_modificacion = fields.DateTime("%Y-%m-%d %H:%M:%S")

class BookExtraServiceReservationSchema(ma.Schema):
    iddef_service = fields.Integer()
    name = fields.String(validate=validate.Length(max=350))
    teaser = fields.String(validate=validate.Length(max=350))
    description = fields.String(validate=validate.Length(max=350))
    icon_description = fields.String(validate=validate.Length(max=350))
    media = fields.List(fields.Nested(publicGetListMedia),dump_only=True)